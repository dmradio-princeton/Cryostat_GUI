#!/usr/bin/env python3

import sys, os
import shutil
import time
import array
import struct

import numpy as np
import matplotlib.pyplot as plt

#import matplotlib.ticker
#from matplotlib.ticker import FuncFormatter, MultipleLocator

from scipy import signal
from scipy.fft import fft, fftfreq
from scipy.fft import rfft, rfftfreq

from Sensoray import Sensoray
from Sensoray import S2608
from Agilent import instrument

from Data import Data

class Measurement:

	def __init__(self,NAME,resplate_temp):
		#initialization of Sensoray
		#Sensoray('10.10.10.1')
		#iomport = 15
		#self.sensoray = S2608(iomport)

		#initialization of Agilent
		self.agilent = instrument("/dev/usbtmc0")

		self.FREQs = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,9,10]

		self.chans = [6,7]
		self.names = ['Agilent','Cryo']

		self.NAME = '{}'.format(NAME)
		self.resplate_temp = resplate_temp

		#remove the previous directory (if exists) and creates the new one
		if os.path.exists(self.NAME):
			shutil.rmtree(self.NAME)
		os.makedirs(self.NAME)

		#array where the amplitude responses for all frequencies are saved:
		#lines correspond to FREQs, columns correspond to: Bx=0, By=1, Bz=2
		self.amplitude_gain = np.zeros((len(self.FREQs), 1))
		self.amplitude = np.zeros((len(self.FREQs), 2))

		#array where the phase shifts for all frequencies are saved:
		#lines correspond to FREQs, columns correspond to: Bx=0, By=1, Bz=2
		self.phase_shift = np.zeros((len(self.FREQs), 1))

		self.square_pulse()

		self.DURATION = 10
		#N = number of points assuming the highest freq = 105 Hz
		self.N = 2*self.DURATION*105+1
		self.SAMPLE_RATE = self.N/self.DURATION

		for self.FREQ in self.FREQs:
			self.f = self.FREQs.index(self.FREQ)
			self.start_agilent()
			self.make_measurement()
			self.process_data()
		self.stop_agilent()

	def square_pulse(self):
		self.DURATION = 400
		#N = number of points assuming the highest freq = 105 Hz
		self.N = 2*self.DURATION*105+1
		self.SAMPLE_RATE = self.N/self.DURATION

		self.FREQ = 0.01

		self.agilent.write("OUTP OFF")
		self.agilent.write("APPL:SQU " + str(float(self.FREQ)) + "," + str(10))
		self.agilent.write("OUTP ON")
		time.sleep(5)

		self.make_measurement()

		for self.chan in self.chans:
			self.k = self.chans.index(self.chan) #number of a column in self.meas array: Agilent=0, Bx=1, By=2, Bz=3
			self.name = self.names[self.k]
					
			field_name = 'FREQ={} Hz, SQUARE_PULSE'.format(self.FREQ)

			dir_path = os.path.join(self.NAME,self.name)
			if not os.path.exists(dir_path):
				os.makedirs(dir_path)

			self.file_path = os.path.join(dir_path, field_name)
			file = open(self.file_path, 'w')
			for i in range(self.T.size):
				file.write(str(self.T[i]) + " " + str(self.meas[:,self.k][i]) + "\n")

			"""plot the signal"""
			plt.plot(self.T, self.meas[:,self.k])
			plt.xlabel('Time [$s$]')
			plt.ylabel('Amplitude [$V$]')
			plt.title('{} Output, at {} Hz'.format(self.name, self.FREQ))
			plt.grid(b=True, which='major', color='#666666', linestyle='-')
			plt.minorticks_on()
			plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
			plt.savefig(self.file_path+'.pdf')
			plt.close()

	def start_agilent(self):
		self.agilent.write("OUTP OFF")
		self.agilent.write("APPL:SIN " + str(float(self.FREQ)) + "," + str(10))
		self.agilent.write("OUTP ON")
		time.sleep(5)

	def stop_agilent(self):
		self.agilent.write("OUTP OFF")
	
	def make_measurement(self):
		'''
		The function measures the magnetometer's voltage corresponding to the magnetic field in three different directions 			and then writes it into the corresponding files. Inputs of the function are: IOMport and channel of Sensoray; 			frequency of the signal, duration of measurement, sampling rate (unless do not exceed the limiting value), and 			the magnetometer's coordinates relative to the reference point. The output of the functions are: three text files 			(for each direction) with two columns each: time [s] and amplitude [V] of the signal; and another three text file 			with two columns each: frequency [Hz] and amplitude [V] of the Fourier transformed signal; also the corresponding 			plots
		'''

		#print('===============================================')
		#print('Sampling rate ~ {:.0f} measurements per second'.format(self.SAMPLE_RATE))
		#print('Number of samples = {}'.format(self.N))
		#print('Duration = {} seconds'.format(self.DURATION))
		#print('===============================================')
		print('Measuring {} Hz'.format(self.FREQ))

		self.meas = np.empty((0, 2))
		self.T = np.zeros(self.N)

		#time step b/w two measurements
		dt = 1/self.SAMPLE_RATE

		#creates time array for all N measurements with the time step dt
		for i in range (self.N):
			self.T[i] =i*dt

		#makes the first measurement and saves time as a reference point
		t0 = time.time()
		self.meas = np.append(self.meas, self.resplate_temp.get_reading_magfield(), axis=0)

		#makes the the rest N-1 measurements
		for i in range (1,self.N):

			#checks if measurements times are alligned with T[i] and waits if the measurements go faster
			t = time.time() - t0 #time of the measurement since the start
			twait = self.T[i] - t #time to wait to be aligned with T[i]

			if twait > 0:
				time.sleep(twait)
			self.meas = np.append(self.meas, self.resplate_temp.get_reading_magfield(), axis=0)
		
	def process_data(self):
		for self.chan in self.chans:
			self.k = self.chans.index(self.chan) #number of a column in self.meas array: Agilent=0, Bx=1, By=2, Bz=3
			self.name = self.names[self.k]

			self.fourier_analyzis()
			#self.check_norm()
			self.write_to_file()
			self.plot()

	def fourier_analyzis(self):
		"""find Fourier transform, normalize, find the amplitude response and the phase shift relative to Agilent"""
		#makes the fast Fourier transformation of the data and plotting it
		self.xf, self.yf = signal.periodogram(self.meas[:,self.k], self.SAMPLE_RATE, scaling = 'spectrum' )

		#self.xf = rfftfreq(self.N,1/self.SAMPLE_RATE)
		#self.yf = rfft(self.meas[:,self.k])
		#self.yf = rfft(self.meas)

		#normalization such that the peak = amplitude/sqrt(2)
		#self.yf_N = np.sqrt(2)*np.abs(self.yf)/self.N
		self.yf_N = np.sqrt(self.yf) #periodogram

		#remove DC component (Earth's field), but save it to add it back later
		self.yf_N0 = self.yf_N[0]
		self.yf_N[0] = 0

		#find the x and y-coordinates of the peak (frequency)
		peak_x = np.argmax(self.yf_N)
		peak_y = self.yf[peak_x]
		
		if self.name == 'Agilent':
			self.signal_peak = peak_y

		else:
			amplitude_gain = np.abs(peak_y/self.signal_peak)
			phase_shift = np.angle(peak_y/self.signal_peak,deg=False)
		
			self.amplitude_gain[self.f,self.k-1] = amplitude_gain
			self.phase_shift[self.f,self.k-1] = phase_shift

		#find the amplitude = peak*sqrt(2) = amplitude
		self.amplitude[self.f,self.k] = np.sqrt(2)*self.yf_N[peak_x]

		#add DC component (Earth's field) back
		self.yf_N[0] = self.yf_N0

	def check_norm(self):
		"""check normalization and Parsevals theorem"""
		print('Check normalization for {}:'.format(self.name))
		RMS = np.sum(np.square(self.meas[:,self.k]))
		RMS_FFT = 2*np.sum(np.square(self.yf_N)) - np.square(self.yf_N[0])

		print('Sq. root of RMS*2 = {}'.format(np.sqrt(2*RMS/self.N)))
		print('Sq. root of  sum of norm. FFTs = {}'.format(np.sqrt(RMS_FFT)))

		print('Parsevals theorem:')
		diff = RMS - (2*np.sum(np.square(np.abs(self.yf))) - np.square(np.abs(self.yf[0])))/self.N
		summ = RMS + (2*np.sum(np.square(np.abs(self.yf))) - np.square(np.abs(self.yf[0])))/self.N
		print('LHS-RHS = {}'.format(diff/summ))
		print('------------------------------------------------')

	def write_to_file(self):
		"""write data to a file"""
		field_name = 'FREQ={} Hz'.format(self.FREQ)

		dir_path = os.path.join(self.NAME,self.name)
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)

		self.file_path = os.path.join(dir_path, field_name)
		self.file_fft_path = os.path.join(dir_path, field_name +"_FFT")

		file = open(self.file_path, 'w')
		file_fft = open(self.file_fft_path, 'w')

		#write the data to a file
		for i in range(self.xf.size):
			file.write(str(self.T[i]) + " " + str(self.meas[:,self.k][i]) + "\n")
			file_fft.write(str(self.xf[i]) + " " + str(np.abs(self.yf_N[i])) + "\n")
		file.close()
		file_fft.close()

		self.file_amplitude_path = os.path.join(dir_path, 'amplitude')
		file_amplitude = open(self.file_amplitude_path, 'a+')
		file_amplitude.write(str(self.FREQ) + " " + str(self.amplitude[self.f,self.k]) + "\n")
		file_amplitude.close()

		if self.name != 'Agilent':
			#self.file_amplitude_path = os.path.join(dir_path, 'amplitude')
			self.file_amplitude_gain_path = os.path.join(dir_path, 'transfer_amplitude_gain')
			self.file_phase_shift_path = os.path.join(dir_path, 'transfer_phase_shift')

			#file_amplitude = open(self.file_amplitude_path, 'a+')
			file_amplitude_gain = open(self.file_amplitude_gain_path, 'a+')
			file_phase_shift = open(self.file_phase_shift_path, 'a+')

			#file_amplitude.write(str(self.FREQ) + " " + str(self.amplitude[self.f,self.k-1]) + "\n")
			file_amplitude_gain.write(str(self.FREQ) + " " + str(self.amplitude_gain[self.f,self.k-1]) + "\n")
			file_phase_shift.write(str(self.FREQ) + " " + str(self.phase_shift[self.f,self.k-1]) + "\n")

			#file_amplitude.close()
			file_amplitude_gain.close()
			file_phase_shift.close()

	def plot(self):
		"""plot the signal"""
		plt.plot(self.T, self.meas[:,self.k])
		plt.xlabel('Time [$s$]')
		plt.ylabel('Amplitude [$V$]')
		plt.title('{} Output, at {} Hz'.format(self.name, self.FREQ))
		plt.grid(b=True, which='major', color='#666666', linestyle='-')
		plt.minorticks_on()
		plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
		plt.savefig(self.file_path+'.pdf')
		plt.close()

		"""plot the fast Fourier transformation"""
		plt.plot(self.xf, self.yf_N)
		plt.xlabel('Frequency [$Hz$]')
		plt.ylabel('Normalized Amplitude Spectrum [$V/\sqrt{Hz}$]')
		plt.title('{} FFT Output, at {} Hz'.format(self.name, self.FREQ))
		plt.grid(b=True, which='major', color='#666666', linestyle='-')
		plt.minorticks_on()
		plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
		plt.savefig(self.file_fft_path+'.pdf')
		plt.close()

		if self.FREQ == self.FREQs[-1]:
			plt.plot(self.FREQs, self.amplitude_gain[:,self.k-1])
			plt.xlabel("Frequency [$Hz$]")
			plt.ylabel('{} Amplitude Gain, '.format(self.name) + '$V_{out}/V_{in}$')
			plt.grid(b=True, which='major', color='#666666', linestyle='-')
			plt.minorticks_on()
			plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
			plt.savefig(self.file_amplitude_gain_path + '.pdf')
			plt.close()

			plt.plot(self.FREQs, self.amplitude[:,self.k])
			plt.xlabel("Frequency [$Hz$]")
			plt.ylabel('{} Amplitude, '.format(self.name) + '$V_{out}$' + " [$V$]")
			plt.grid(b=True, which='major', color='#666666', linestyle='-')
			plt.minorticks_on()
			plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
			plt.savefig(self.file_amplitude_path + '.pdf')
			plt.close()

			fig, ax = plt.subplots()
			ax.plot(self.FREQs, self.phase_shift[:,self.k-1])
			plt.xlabel("Frequency [$Hz$]")
			plt.ylabel('{} Phase Shift, '.format(self.name) + 'rad')
			labels = [r'$-\pi$', r'$-3\pi/4$', r'$-\pi/2$', r'$-\pi/4$', '$0$', r'$\pi/4$', r'$\pi/2$', r'$3\pi/4$', r'$\pi$']
			ax.set_yticks(np.arange(-np.pi, np.pi+0.01, np.pi/4))
			ax.set_yticklabels(labels)
			plt.grid(b=True, which='major', color='#666666', linestyle='-')
			plt.minorticks_on()
			plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
			plt.savefig(self.file_phase_shift_path + '.pdf')
			plt.close()
