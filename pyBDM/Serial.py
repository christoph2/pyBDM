#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__="0.1.0"

__copyright__="""
    pyBDM - Library for the Motorola/Freescale Background Debugging Mode.

   (C) 2010-2011 by Christoph Schueler <github.com/Christoph2,
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

import Port
import serial
import sys
import types


class Port(Port.Port):
    def __init__(self,num,baudrate,bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=0.1):
        self.port=None
        try:
            self.port=serial.Serial(port=num,baudrate=baudrate,bytesize=bytesize,
                parity=parity,stopbits=stopbits,timeout=timeout)
        except serial.SerialException,e:
            print sys.exc_info
            raise e
#        print "OK, openend as '%s' @ %d Bits/Sec." % (self.port.portstr,self.port.baudrate)

    def __del__(self):
        if self.port and self.port.isOpen()==True:
            self.port.close()
#            print "Closed COM-Port."

    def write(self,data):
        if not isinstance(data,(types.ListType,types.TupleType)):
            data=[data]
        self.port.write(bytearray(data))

    def read(self,len):
        data=self.port.read(len)
        return bytearray(data)


def main():
    pass

if __name__=='__main__':
    main()
