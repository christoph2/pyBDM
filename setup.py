#!/bin/env/python

from setuptools import setup	#,find_packages

setup(
    name='pyBDM',
    version='0.1',
    description="'pyBDM'-Distribution",
    author='Christoph Schueler',
    author_email='cpu12.gems@googlemail.com',
    url='http://www.github.com/Christoph2/pyBDM',
    packages=['pyBDM'], #'PyBDM/s12'],
    entry_points = {
	'console_scripts': [
		'bdm_partinfo = pyBDM.scripts.bdm_partinfo:main'
#	    'foo = my_package.some_module:main_func',
#	    'bar = other_module:some_func',
        ],
    },
    install_requires=[
	'pyserial', 'mock', 'enum34'
    ],
    test_suite = "tests"
)

