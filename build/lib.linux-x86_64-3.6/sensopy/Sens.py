"""
Module for interacting with the sensoray python extension.
Only really useful for working with a main module connected
to 2608's.

Author: Lucas Parker
E-mail: thelucasparker@gmail.com
"""

import sys, os
import time
import array
import struct

from scipy.fft import fft, fftfreq
from scipy.fft import rfft, rfftfreq

from scipy import signal
import math

import numpy as np
import matplotlib.pyplot as plt

from sensopy import _sensopy

from collections import namedtuple
Pair = namedtuple("Pair", ["t", "v"])
pairs = [Pair(400.0, 0.27456), Pair(300.0, 0.51892), Pair(24.0, 1.13698), Pair(10.0, 1.42014), Pair(1.4,1.69812), Pair(1.0,1.80)]

class Sensoray:
	"""
	Initialize sensoray and interact with 2608 modules.
	self[iomport] will be an S2608 object.
	"""
	def __init__(self, ip_addr, bad_val=None):
		"""
		ip_addr should be a string.
		"""
		self._s2608_iomports = _sensopy.init_sensoray(ip_addr)
		if len(self._s2608_iomports) == 0:
			raise Exception("No 2608 iomports found.")
		self._s2608s = {}
		for iomport in self._s2608_iomports:
			self._s2608s[iomport] = S2608(iomport, bad_val=bad_val)
		self._ain_files = [ self[iomport]._ain_files for iomport in self._s2608s ]

		# parameters for writing dirfile eventually:
		self._nsamp = 0
		self._spf = 1

		parent_dir=''
		dfname = str(int(time.time()))
		self.dirname = os.path.join(parent_dir, dfname)

	def __getitem__(self, iomport):
		return self._s2608s[iomport]

	def get_all_ains(self):
		"""
		Return dictionary of all ains. Keys are iomport number.
		"""
		return _sensopy.get_multiple_2608_ains(self._s2608_iomports)

	def write_all_ains(self, autoflush=True):
		_sensopy.write_multiple_2608_ains(self._ain_files)
		self._nsamp += 1
		if autoflush and self._nsamp % self._spf == 0:
			self.flush_all_ain_files()

	def flush_all_ain_files(self):
		for iomport in self._s2608s:
			self[iomport].flush_ain_files()

	def start_default_dirfile(self, fsamp=1000000000, spf=50): #good for 10Hz
		"""
		Open a dirfile, where files are named by iomport and channel.
		If no dfname (directory to create for new dirfile) is provided,
		it will be named after the current ctime.
		The dirfile will be created in parent_dir (current dir if no parent_dir is provided).
		spf is samples per frame. ain_files will be flushed after this many samples for nice kst plotting, maybe.
		Sampling will happen at approximately fsamp speed (as long as it isn't too fast!)
		Time stamps will be written to the 'time' field.
		"""
		#self.dirname = os.path.join(parent_dir, dfname)

		if os.path.isdir(self.dirname):
			raise Exception('Cannot create dirfile %s. A directory already exists there.\n' % self.dirname)	
		os.mkdir(self.dirname)
		field_names = []
		for iomport in self._s2608s:
                    for chan in range(16):
                        field_names += self[iomport].open_default_files(dirname=self.dirname,chan=chan)
		fmt_file = open(os.path.join(self.dirname, 'format'), 'w')
		for field_name in field_names:
			fmt_file.write('%s RAW FLOAT64 %d\n' % (field_name, spf,))
		fmt_file.write('time RAW FLOAT64 %d\n' % spf)
		fmt_file.write('/REFERENCE time\n')
		fmt_file.close()

		self._nsamp = 0
		self._spf = spf

		t_array = array.array('d', [0.0]*spf)
		tfile = open(os.path.join(self.dirname, 'time'), 'w')

		dt = 1/fsamp
		t0 = time.time()
		i = 0
		try:
			while True:
				twait = t0 + self._nsamp*dt - time.time()
				if twait > 0:
					time.sleep(twait)
				self.write_all_ains(autoflush=False)
				t_array[i] = time.time()
				i += 1

				if i % self._spf == 0:
					i = 0
					self.flush_all_ain_files()
					for k in range(self._spf):
						tfile.write(str(t_array[k])+"\n")
					tfile.flush()
		except KeyboardInterrupt:
			pass
		

class S2608:
	def __init__(self, iomport, bad_val=None):
		"""
		bad_val is number written for failed samples.
		It will be MIN_DBL if bad_val=None.
		"""
		self._iomport = iomport

		## need to call get_caldata before you should get ains.
		if bad_val is None:
			self._ain_files = _sensopy.init_2608_ain_files(self._iomport)
		else:
			self._ain_files = _sensopy.init_2608_ain_files(self._iomport, bad_val)
		self.get_caldata()

	def get_caldata(self):
		_sensopy.get_2608_caldata(self._iomport)
	
	def get_aout(self, chan):
		return _sensopy.get_2608_aout(self._iomport, chan)

	def set_aout(self, chan, volts):
		_sensopy.set_2608_aout(self._iomport, chan, volts)

	def get_ains(self):
		return _sensopy.get_2608_ains(self._iomport)

	def get_ain(self, chan):
		return _sensopy.get_2608_ain(self._iomport, chan)

	def get_2ains_magnet(self,chan1, chan2):
		return _sensopy.get_2608_2ains_magnet(self._iomport, chan1, chan2)

	def get_4ains_magnet(self,chan1, chan2, chan3, chan4):
		return _sensopy.get_2608_4ains_magnet(self._iomport, chan1, chan2, chan3, chan4)

	def get_5ains_magnet(self,chan1, chan2, chan3, chan4, chan5):
		return _sensopy.get_2608_5ains_magnet(self._iomport, chan1, chan2, chan3, chan4, chan5)

	def open_ain_file(self, fname, channel):
		"""
		Open file which will recieve channel's data.
		"""
		_sensopy.open_2608_ain_file(self._ain_files, fname, channel)

	def write_ains(self):
		"""
		Sample 2608 and write to opened ain files.
		"""
		_sensopy.write_2608_ains(self._ain_files)

	def flush_ain_files(self):
		_sensopy.flush_2608_ain_files(self._ain_files)

	def open_default_files(self, dirname='', chan=0):
		field_name = 'iomport%02d_chan%02d' % (self._iomport, chan)
		self.open_ain_file(os.path.join(dirname, field_name), chan)
		return field_name

	def get_reading(self, chan):
		if chan == 6 and self._iomport == 7:
			return self.v_to_p(self.get_ains()[chan])
		else:
			return self.v_to_t(self.get_ains()[chan])
