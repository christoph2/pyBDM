#!/bin/env/python

from setuptools import setup	#,find_packages

setup(
    name='pyBDM',
    version='0.1',
    description="'pyBDM'-Distribution",
    author='Christoph Schueler',
    author_email='cpu12.gems@googlemail.com',
    url='http://www.github.com/Christoph2/pyBDM',
    packages=['pyBDM', 'PyBDM/S12'],
#    entry_points = {
#	'console_scripts': [
#	    'foo = my_package.some_module:main_func',
#	    'bar = other_module:some_func',
#        ],
#    }

    install_requires=['pyserial', 'puremvc'
    ],
#    scripts=[
#    ]
)

