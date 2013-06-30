#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__="0.1.0"

__copyright__="""
    pyBDM - Library for the Motorola/Freescale Background Debugging Mode.

   (C) 2010-2013 by Christoph Schueler <github.com/Christoph2,
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

import abc
import logging
from S12.BdmModule import Bdm

##
##  BMD-Commands.
##
"""
BACKGROUND      90  None
    Enter background mode if ?rmware is enabled. If enabled, an ACK will be issued when the part enters active background mode.
ACK_ENABLE      D5  None
    Enable Handshake. Issues an ACK pulse after the command is executed.
ACK_DISABLE     D6  None
    Disable Handshake. This command does not issue an ACK pulse.
READ_BD_BYTE    E4  16-bit address  16-bit data out
    Read from memory with standard BDM ?rmware lookup table in map. Odd address data on low byte; even address data on high byte.
READ_BD_WORD    EC  16-bit address  16-bit data out
    Read from memory with standard BDM ?rmware lookup table in map. Must be aligned access.
READ_BYTE       E0  16-bit address  16-bit data out
    Read from memory with standard BDM ?rmware lookup table out of map. Odd address data on low byte; even address data on high byte.
READ_WORD       E8  16-bit address  16-bit data out
    Read from memory with standard BDM ?rmware lookup table out of map. Must be aligned access.
WRITE_BD_BYTE   C4  16-bit address  16-bit data in
    Write to memory with standard BDM ?rmware lookup table in map. Odd address data on low byte; even address data on high byte.
WRITE_BD_WORD   CC  16-bit address  16-bit data in
    Write to memory with standard BDM ?rmware lookup table in map. Must be aligned access.
WRITE_BYTE      C0  16-bit address  16-bit data in
    Write to memory with standard BDM ?rmware lookup table out of map. Odd address data on low byte; even address data on high byte.
WRITE_WORD      C8  16-bit address  16-bit data in
    Write to memory with standard BDM ?rmware lookup table out of map. Must be aligned access.
"""

# BDM Hardware Commands.
BACKGROUND      = 0x90 # Enter background mode if firmware enabled.
READ_BD_BYTE    = 0xE4 # Read from memory with BDM in map.
READ_BD_WORD    = 0xEC # Read from memory with BDM in map.
READ_BYTE       = 0xE0 # Read from memory with BDM out of map.
READ_WORD       = 0xE8 # Read from memory with BDM out of map.
WRITE_BD_BYTE   = 0xC4 # Write to memory with BDM in map.
WRITE_BD_WORD   = 0xCC # Write to memory with BDM in map.
WRITE_BYTE      = 0xC0 # Write to memory with BDM out of map.
WRITE_WORD      = 0xC8 # Write to memory with BDM out of map.

# BDM Firmware Commands.
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

abstractmethod = abc.abstractmethod

MEMORY_HIGH     = 0xffff

##
## Interrupt vectors available on every HC(S)12.
##
IRQ_VECTOR      = 6
XIRQ_VECTOR     = 5
SWI_VECTOR      = 4
TRAP_VECTOR     = 3
COP_VECTOR      = 2
CMF_VECTOR      = 1
RESET_VECTOR    = 0


PPAGE           = 0x30

from collections import namedtuple
MemorySizes = namedtuple('MemorySizes','regSpace eepSpace ramSpace allocRomSpace')

logger = logging.getLogger("pyBDM")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s[%(levelname)s]: %(message)s","%Y-%m-%d %H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)

class CommunicationError(Exception): pass

class Device(object):
    __metaclass__= abc.ABCMeta
    DEVICE_NAME = None
    VARIABLE_BUS_FREQUENCY = False

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger("pyBDM")
        super(Device,self).__init__(*args, **kwargs)
        self.bdmModule = Bdm(self)

    @abstractmethod
    def reset(self):
        self.logger.debug("Resetting Target.")

# BDM Hardware Commands.
    def targetGo(self):
        self.logger.debug("GO")
        self.__writeCommand__(GO)

    def targetTagGo(self):
        self.logger.debug("TAGGO")
        self.__writeCommand__(TAGGO)

    def targetHalt(self):
        self.logger.debug("BACKGROUND")
        self.__writeCommand__(BACKGROUND)

    def targetTrace(self):
        self.logger.debug("TRACE1")
        self.__writeCommand__(TRACE1)

# BDM Firmware Commands.
    def readBDWord(self, addr):
        self.logger.debug("READ_BD_WORD[0x%04x]" % addr)
        data=self.__readWord__(READ_BD_WORD, addr)
        self.logger.debug("RESULT: 0x%04x" % data)
        return data

    def readWord(self, addr):
        self.logger.debug("READ_WORD[0x%04x]" % addr)
        data = self.__readWord__(READ_WORD, addr)
        self.logger.debug("RESULT: 0x%04x" % data)
        return data

    def readBDByte(self, addr):
        self.logger.debug("READ_BD_BYTE[0x%04x]" % addr)
        data = self.__readCommand__(READ_BD_BYTE, 1, addr)[0]
        self.logger.debug("RESULT: 0x%02x" % data)
        return data

    def readByte(self, addr):
        self.logger.debug("READ_BYTE[0x%04x]" % addr)
        data = self.__readCommand__(READ_BYTE, 1, addr)[0]
        self.logger.debug("RESULT: 0x%02x" % data)
        return data

    def writeBDWord(self, addr, data):
        self.logger.debug("WRITE_BD_WORD[0x%04x]=0x%04x" % (addr, data))
        self.__writeWord__(WRITE_BD_WORD, addr, data)

    def writeBDByte(self, addr, data):
        self.logger.debug("WRITE_BD_BYTE[0x%04x]=0x%02x" % (addr, data))
        self.__writeByte__(WRITE_BD_BYTE,addr, data)

    def writeByte(self, addr, data):
        self.logger.debug("WRITE_BYTE[0x%04x]=0x%02x" % (addr, data))
        self.__writeByte__(WRITE_BYTE, addr, data)

    def writeWord(self, addr, data):
        self.logger.debug("WRITE_WORD[0x%04x]=0x%04x" % (addr, data))
        self.__writeWord__(WRITE_WORD, addr, data)

    def readNext(self):
        self.logger.debug("READ_NEXT")
        return self.__readWord__(READ_NEXT)

    def writeNext(self,data):
        self.logger.debug("WRITE_NEXT[0x%04x]" % data)
        self.__writeWord__(WRITE_NEXT, data)

    def readPC(self):
        self.logger.debug("READ_PC")
        return self.__readWord__(READ_PC)

    def readD(self):
        self.logger.debug("READ_D")
        return self.__readWord__(READ_D)

    def readX(self):
        self.logger.debug("READ_X")
        return self.__readWord__(READ_X)

    def readY(self):
        self.logger.debug("READ_Y")
        return self.__readWord__(READ_Y)

    def readSP(self):
        self.logger.debug("READ_SP")
        return self.__readWord__(READ_SP)

    def writePC(self, data):
        self.logger.debug("WRITE_PC[0x%04x]", data)
        self.__writeWord__(WRITE_PC, data)

    def writeD(self, data):
        self.logger.debug("WRITE_D[0x%04x]", data)
        self.__writeWord__(WRITE_D, data)

    def writeX(self, data):
        self.logger.debug("WRITE_X[0x%04x]", data)
        self.__writeWord__(WRITE_X, data)

    def writeY(self, data):
        self.logger.debug("WRITE_Y[0x%04x]", data)
        self.__writeWord__(WRITE_Y, data)

    def writeSP(self, data):
        self.logger.debug("WRITE_SP[0x%04x]", data)
        self.__writeWord__(WRITE_SP, data)

##
## Convenience Methods.
##
    def readCCR(self):
        return self.bdmModule.ccrHolding

    def writeCCR(self, value):
        self.bdmModule.ccrHolding = value

    def getPartID(self):
        """Note: the 'classic' HC12 derivates don't have PartID-Registers! """
        return self.readWord(0x001a)

    def getMemorySizes(self):
        """Note: the 'classic' HC12 derivates don't have MEMSIZE-Registers! """
        EEP_MAP = {0: 0, 1: 2*1024, 2: 4*1024, 3: 8*1024}
        RAM_MAP = {0: 2*1024, 1: 4*1024, 2: 6*1024, 3: 8*1024, 4: 10*1024, 5: 12*1024, 6: 14*1024, 7: 16*1024}
        ROM_MAP = {0: 0*1024, 1: 16*1024, 2: 48*1024, 3: 64*1024}
        memSize = self.readWord(0x001c)
        regSpace = (memSize & 0x8000) >> 15
        if regSpace == 1:
            regSpace = 2
        else:
            regSpace = 1
        regSpace *= 1024

        eepSpace = EEP_MAP[(memSize & 0x3000) >> 12]
        ramSpace = RAM_MAP[(memSize & 0x0700) >> 8]
        allocRomSpace = ROM_MAP[(memSize & 0x00C0) >> 6]
        pageSpace = (memSize & 0x0003)

        return MemorySizes(regSpace, eepSpace, ramSpace, allocRomSpace)


    def readArea(self, addr, length):
        if length == 0:
            return None
        loops = length / self.MAX_READ_PAYLOAD
        bytesRemaining = length % self.MAX_READ_PAYLOAD
        offset = addr
        result = bytearray()
        for l in range(loops):
            self.logger.debug("Reading %u bytes starting @ 0x%04x." % (self.MAX_READ_PAYLOAD, offset))
            data = self.__readArea__(offset, self.MAX_READ_PAYLOAD)
            result.extend(data)
            offset += self.MAX_READ_PAYLOAD
        if bytesRemaining:
            self.logger.debug("Reading %u bytes starting @ 0x%04x." % (bytesRemaining, offset))
            data = self.__readArea__(offset,bytesRemaining)
            result.extend(data)
        return result

    def fillArea(self, addr, value, length):
        if length == 0:
            return
        loops = length / self.MAX_WRITE_PAYLOAD
        bytesRemaining = length % self.MAX_WRITE_PAYLOAD
        offset = addr
        for l in range(loops):
            self.logger.debug("Filling %u bytes with 0x%02x starting @ 0x%04x." % (self.MAX_WRITE_PAYLOAD, value, offset))
            self.__writeArea__(offset, self.MAX_WRITE_PAYLOAD, [value] * self.MAX_WRITE_PAYLOAD)
            offset += self.MAX_WRITE_PAYLOAD
        if bytesRemaining:
            self.logger.debug("Filling %u bytes with 0x%02x starting @ 0x%04x." % (bytesRemaining, value, offset))
            self.__writeArea__(offset, bytesRemaining, [value] * bytesRemaining)

    def writeArea(self, addr, data):
        length = len(data)
        if length == 0:
            return None
        loops = length / self.MAX_WRITE_PAYLOAD
        bytesRemaining = length % self.MAX_WRITE_PAYLOAD
        addrOffset = addr

        dataOffsetFrom = 0
        dataOffsetTo = self.MAX_WRITE_PAYLOAD
        for l in range(loops):
            self.logger.debug('Writing %u bytes starting @ 0x%04x.' % (self.MAX_WRITE_PAYLOAD, addrOffset))
            slice = data[dataOffsetFrom : dataOffsetTo]
            self.__writeArea__(addrOffset, self.MAX_WRITE_PAYLOAD, slice)
            addrOffset += self.MAX_WRITE_PAYLOAD
            dataOffsetFrom = dataOffsetTo
            dataOffsetTo = dataOffsetFrom + self.MAX_WRITE_PAYLOAD
        if bytesRemaining:
            self.logger.debug('Writing %u bytes starting @ 0x%04x.' % (bytesRemaining, addrOffset))
            slice = data[dataOffsetFrom: dataOffsetFrom + bytesRemaining]
            self.__writeArea__(addrOffset, bytesRemaining, slice)

    def getPPage(self):
        return self.readBDByte(PPAGE)

    def setPPage(self, value):
        self.writeBDByte(PPAGE, value)

    def getVector(self, vectorNumber):
        addr = MEMORY_HIGH - (2 * vectorNumber) - 1
        content = self.readWord(addr)
        return content

    def getResetVector(self):
        return self.getVector(RESET_VECTOR)

    def getCMFVector(self):
        return self.getVector(CMF_VECTOR)

    def getCOPVector(self):
        return self.getVector(COP_VECTOR)

    def getTrapVector(self):
        return self.getVector(TRAP_VECTOR)

    def getSWIVector(self):
        return self.getVector(SWI_VECTOR)

    def getXIRQVector(self):
        return self.getVector(XIRQ_VECTOR)

    def getIRQVector(self):
        return self.getVector(IRQ_VECTOR)


