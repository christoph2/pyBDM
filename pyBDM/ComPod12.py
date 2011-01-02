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

import BDM
import Serial

from BDM import Device
from Port import Port

##
##  BMD-Commands.
##

RESET           = 0x80 # Reset
FILL_AREA       = 0x82 # FILL_AREA ADDR_HI ADDR_LO CNT DATA
READ_AREA       = 0x83 # READ_AREA ADDR_HI ADDR_LO CNT (0==0xff)
VERSION         = 0xFF


BACKGROUND      = 0x90 # Enter background mode if firmware enabled.
READ_BD_BYTE    = 0xE4 # Read from memory with BDM in map.
READ_BD_WORD    = 0xEC # Read from memory with BDM in map.
READ_BYTE       = 0xE0 # Read from memory with BDM out of map.
READ_WORD       = 0xE8 # Read from memory with BDM out of map.
WRITE_BD_BYTE   = 0xC4 # Write to memory with BDM in map.
WRITE_BD_WORD   = 0xCC # Write to memory with BDM in map.
WRITE_BYTE      = 0xC0 # Write to memory with BDM out of map.
WRITE_WORD      = 0xC8 # Write to memory with BDM out of map.
READ_NEXT       = 0x62 # X = X + 2; Read next word pointed to by X
READ_PC         = 0x63 # Read program counter.
READ_D          = 0x64 # Read D accumulator.
READ_X          = 0x65 # Read X index register.
READ_Y          = 0x66 # Read Y index register.
READ_SP         = 0x67 # Read stack pointer.
WRITE_NEXT      = 0x42 # X = X + 2; Write next word pointed to by X
WRITE_PC        = 0x43 # Write program counter.
WRITE_D         = 0x44 # Write D accumulator.
WRITE_X         = 0x45 # Write X index register.
WRITE_Y         = 0x46 # Write Y index register.
WRITE_SP        = 0x47 # Write stack pointer.
GO              = 0x08 # Go to user program.
TRACE1          = 0x10 # Execute one user instruction then return to BDM.
TAGGO           = 0x18 # Enable tagging and go to user program.


class NoResponseError(Exception): pass
class InvalidResponseError(Exception): pass

def com(v):
    return 0xff & ~v

class ComPod12(Device,Serial.Port):
    MAX_PAYLOAD=0xff
    DEVICE_NAME="Elektronik-Laden ComPOD12"

    def close(self):
        self.port.close()

    def __writeCommand__(self,cmd,responseLen):
        self.write(cmd)
        data=self.read(responseLen)
        if data==bytearray():
            raise NoResponseError
        if data[0]!=com(cmd):
            raise InvalidResponseError
        if len(data)>1:
            return data[1:]
        else:
            return None

    def __readCommand__(self,cmd,responseLen,addr=None):
        self.write(cmd)
        if not addr is None:
            self.write((addr>>8) & 0xff)
            self.write(addr & 0xff)
        data=self.read(responseLen)
        if data==bytearray():
            raise NoResponseError
        if len(data)!=responseLen:
            raise InvalidResponseError
        return data
    
    def __readWord__(self,cmd,addr=None):
        data=self.__readCommand__(cmd,2,addr)
        if data==bytearray():
            raise NoResponseError
        if len(data)!=2:
            raise InvalidResponseError
        return data[0]<<8 | data[1]

    def __writeWord__(self,cmd,data0,data1=None):
        self.write(cmd)
        self.write((data0>>8) & 0xff)
        self.write(data0 & 0xff)
        if data1:
            self.write((data1>>8) & 0xff)
            self.write(data1 & 0xff)
        d=self.read(1)
        if d==bytearray():
            raise NoResponseError
        if (d[0]!=com(cmd)):
            raise InvalidResponseError

    def __writeByte__(self,cmd,addr,data):
        self.write(cmd)
        self.write((addr>>8) & 0xff)
        self.write(addr & 0xff)
        self.write(data)
        d=self.read(1)
        if d==bytearray():
            raise NoResponseError
        if (d[0]!=com(cmd)):
            raise InvalidResponseError

    def reset(self):
        self.__writeCommand__(RESET,1)

    def getPODVersion(self):
        data=self.__readCommand__(VERSION,2)
        return "%s v%02u.%02u" % (self.DEVICE_NAME,data[0],data[1])

    def targetGo(self):
        self.__writeCommand__(GO,1)

    def targetTagGo(self):
        self.__writeCommand__(TAGGO,1)

    def targetHalt(self):
        self.__writeCommand__(BACKGROUND,1)

    def targetTrace(self):
        self.__writeCommand__(TRACE1,1)

    def readBDWord(self,addr):
        return self.__readWord__(READ_BD_WORD,addr)

    def readWord(self,addr):
        return self.__readWord__(READ_WORD,addr)

    def readBDByte(self,addr):
        data=self.__readCommand__(READ_BD_BYTE,1,addr)
        return data[0]

    def readByte(self,addr):
        data=self.__readCommand__(READ_BYTE,1,addr)
        return data[0]

    def readNext(self):
        return self.__readWord__(READ_NEXT)

    def readPC(self):
        return self.__readWord__(READ_PC)

    def readD(self):
        return self.__readWord__(READ_D)

    def readX(self):
        return self.__readWord__(READ_X)

    def readY(self):
        return self.__readWord__(READ_Y)
        
    def readSP(self):
        return self.__readWord__(READ_SP)

    def readCCR(self):
        return self.readBDByte(0xff06)

    def writePC(self,data):
        self.__writeWord__(WRITE_PC,data)

    def writeD(self,data):
        self.__writeWord__(WRITE_D,data)

    def writeX(self,data):
        self.__writeWord__(WRITE_X,data)

    def writeY(self,data):
        self.__writeWord__(WRITE_Y,data)

    def writeSP(self,data):
        self.__writeWord__(WRITE_SP,data)

    def writeCCR(self,data):
        return self.WriteBDByte(0xff06,data)

    def writeBDWord(self,addr,data):
        self.__writeWord__(WRITE_BD_WORD,addr,data)

    def writeWord(self,addr,data):
        self.__writeWord__(WRITE_WORD,addr,data)

    def writeBDByte(self,addr,data):
        self.__writeByte__(WRITE_BD_BYTE,addr,data)

    def writeByte(self,addr,data):
        self.__writeByte__(WRITE_BYTE,addr,data)

    def writeNext(self,data):
        self.__writeWord__(WRITE_NEXT,data)

    def __readArea__(self,addr,length):
        self.write(READ_AREA)
        self.write((addr>>8) & 0xff)
        self.write(addr & 0xff)
        self.write(length)
        data=self.read(length)
        if len(data)==0:
            raise NoResponseError
        if len(data)!=length:
            raise InvalidResponseError
        return data

    def readArea(self,addr,length):
        if length==0:
            return None
        loops=length / self.MAX_PAYLOAD
        bytesRemaining=length % self.MAX_PAYLOAD
        offset=addr
        result=bytearray()
        for l in range(loops):
            data=self.__readArea__(offset,self.MAX_PAYLOAD)
            result.extend(data)
            offset+=self.MAX_PAYLOAD
        if bytesRemaining:
            data=self.__readArea__(offset,bytesRemaining)
            result.extend(data)
        return result

    def __fillArea__(self,addr,length,data):
        self.write(FILL_AREA)
        self.write((addr>>8) & 0xff)
        self.write(addr & 0xff)
        self.write(length)
        self.write(data)
        data=self.read(1)
        print
        '''
        if len(data)==0:
            raise NoResponseError
        '''