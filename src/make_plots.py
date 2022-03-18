#!/usr/bin/env python3

import sys, os
import time
import array

import numpy as np
import matplotlib.pyplot as plt

FREQs = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5,6,7,8,9,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]

data_dir = '/home/dmradio/Desktop/cryostat_shield_test_cooldown3/src'
Amp_dir = '/Cryo/amplitude'

NO_SHIELD_resplate = 'NO_SHIELD_resplate' +  Amp_dir
CRYOPERM =  'CRYOPERM_X10AMP_1' + Amp_dir
FortyKSHIELD = '40KSHIELD_X10AMP_1' + Amp_dir
MuMetalSHIELD = 'MuMetalSHIELD_X100AMP_1' + Amp_dir
VacuumeSHIELD = 'VacuumSHIELD_X200AMP_1' + Amp_dir

names = [\
NO_SHIELD_resplate,\
CRYOPERM,\
FortyKSHIELD,\
MuMetalSHIELD,\
VacuumeSHIELD\
]

labels = [\
'NO_SHIELD_resplate',\
'CRYOPERM',\
'40KSHIELD',\
'MuMetalSHIELD',\
'VacuumSHIELD'\
]


fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()
k = 0
for name in names:
	LABEL = labels[k]
	AMPLIFICATION = False
	BASE_LINE = False

	#if name == NO_SHIELD_resplate:
	if k == 0:
		BASE_LINE = True
	k += 1

	if 'AMP_1' in name:
		AMPLIFICATION = True
		factor = ''
		index = name.find('AMP_1')-1
		while index > 0:
			if name[index].isnumeric():
				factor = name[index] + factor
				index -= 1
			else:
				factor = float(factor)
				break

	file = open(name, 'r')
	lines = file.readlines()
	data = np.zeros((19,2))

	for line in lines:
		i = lines.index(line)
		if i < 19:
			data[i,0] = line.split()[0]
			data[i,1] = line.split()[1]

		if AMPLIFICATION == True:
			data[i,1] = data[i,1]/factor

	if BASE_LINE == True:
		base = data

	print('DC attenuation ={:.5f} for {}'.format(data[0,1]/base[0,1], LABEL))
	print('AC attenuation ={:.5f} for {}'.format(data[-1,1]/base[-1,1], LABEL))

	"""plot the signal"""
	ax1.loglog(data[:,0], data[:,1], label=LABEL)
	ax2.loglog(data[:,0], np.divide(data[:,1], base[:,1]), label=LABEL)

	ax1.set_xlabel('Frequency [$Hz$]')
	ax1.set_ylabel('Amplitude [$V$]')
	ax1.grid(b=True, which='major', color='#666666', linestyle='-')
	ax1.minorticks_on()
	ax1.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
	ax1.legend(bbox_to_anchor=(1.04,1), borderaxespad=0)
	fig1.savefig('Amplitudes.pdf', dpi=fig1.dpi, bbox_inches="tight")

	ax2.set_xlabel('Frequency [$Hz$]')
	ax2.set_ylabel('Attenuation')
	ax2.grid(b=True, which='major', color='#666666', linestyle='-')
	ax2.minorticks_on()
	ax2.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
	ax2.legend(bbox_to_anchor=(1.04,1), borderaxespad=0)
	fig2.savefig('Attenuation.pdf', dpi=fig2.dpi, bbox_inches="tight")
