#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

__copyright__ = \
    """
    pyBDM - Library for the Motorola/Freescale Background Debugging Mode.

   (C) 2010-2016 by Christoph Schueler <github.com/Christoph2,
                                        cpu12.gems@googlemail.com>

   All Rights Reserved

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from pyBDM.logger import Logger
from pyBDM.utils import setBits, clearBits, bitsSet

__all__ = ['Module']


def registerProperty(name, registerAddress, eightBit = True, doc = None):
    def fget8( self):
        return self.read8(registerAddress)

    def fset8(self, value):
        self.write8(registerAddress, value)

    def fget16( self):
        return self.read16(registerAddress)

    def fset16(self, value):
        self.write16(registerAddress, value)

    if eightBit:
        return property(fget = fget8, fset = fset8, doc = doc)
    else:
        return property(fget = fget16, fset = fset16, doc = doc)


class Module(object):

    def __init__(self, port):
        self._port = port
        self.logger = Logger()
        if hasattr(self, '__REGISTERS8__'):
            for name, reg in self.__REGISTERS8__:
                setattr(self.__class__, name, registerProperty(name, reg, True))
        if hasattr(self, '__REGISTERS16__'):
            for name, reg in self.__REGISTERS16__:
                setattr(self.__class__, name, registerProperty(name, reg, False))

    def read8(self, addr):
        return self.port.readBDByte(addr)

    def write8(self, addr, value):
        self.port.writeBDByte(addr, value)

    def read16(self, addr):
        return self.port.readBDWord(addr)

    def write16(self, addr, value):
        self.port.writeBDWord(addr, value)

    def setRegisterBits(self, register, mask):
        value = setBits(register, mask)
        register = value

    def clearRegisterBits(self, register, mask):
        value = clearBits(register, mask)
        register = value

    def registerBitsSet(self, register, mask):
        return bitsSet(register, mask)

    def _getPort(self):
        return self._port

    port = property(_getPort)

