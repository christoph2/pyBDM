#!/bin/env/python

from distutils.core import setup,Extension
from setuptools import find_packages

setup(
    name='pyBDM',
    version='0.1',
    description="'pyBDM'-Distribution",
    author='Christoph Schueler',
    author_email='cpu12.gems@googlemail.com',
    url='http://www.github.com/Christoph2/k-os',
    packages=['pyBDM'],
#    package_dir={
#	"k_osek" : "."
#    },
    scripts=[
#    "./sysgen/kosgen.py",
    ]
    # py_modules=['foo'],
#    ext_modules=[Extension('foo', ['foo.i','foo.c'])],
)

