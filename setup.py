#!/usr/bin/env python
from distutils.core import setup, Extension
import os

if not os.path.isfile('api/linux/lib2600.a'):
	os.system('cd api/linux/ && make')

sensopy_ext = Extension('sensopy._sensopy',
	sources=['src/sensopy.c',],
	include_dirs = ['api/common', 'api/linux',],
	library_dirs = ['api/linux',],
	libraries = ['2600',],
	extra_compile_args=['-std=c99',],
)

setup(name='GUI_DMRadio',
	version='0.0',
	author='',
	description='',
	package_dir={'sensopy': 'src'},
	packages=['sensopy',],
	ext_modules=[sensopy_ext,],
)

