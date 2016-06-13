#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1.0"

__copyright__ = """
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

import port
import serial
import types

class PortException(serial.SerialException): pass
from pyBDM.utils import slicer

def dumpa(arr):
    return [s for s in slicer(arr, 2)]

class Port(port.Port):
    def __init__(self, num, baudrate, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE,
            timeout = 0.1):
        self.port = None
        self.num = num
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout

    def connect(self):
        try:
            self.port = serial.Serial(port = self.num, baudrate = self.baudrate, bytesize = self.bytesize, parity = self.parity,
                stopbits = self.stopbits, timeout = self.timeout
            )
        except serial.SerialException as e:
            raise PortException(e)

#        print("OK, openend as '%s' @ %d Bits/Sec." % (self.port.portstr,self.port.baudrate))

    def __del__(self):
        if self.port and self.port.isOpen() == True:
            self.port.close()
#            print("Closed COM-Port.")

    def write(self, data):
        if not isinstance(data, (types.ListType, types.TupleType)):
            data = [data]
        self.port.write(bytearray(data))
        #self.port.flush()

    def read(self, length):
        data = self.port.read(length)
        #return bytearray(data)
        #print("Serial::read: '%s' [%s]." % (dumpa(data), hexDump(bytearray(data))))
        #self.port.flush()
        return bytearray(data)

    def close(self):
        if self.port and not self.port.closed:
            self.port.close()

