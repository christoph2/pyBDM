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

import abc
from pyBDM.s12.BdmModule import Bdm
from pyBDM.logger import Logger

##
##  BMD-Commands.
##

# BDM Hardware Commands.
BACKGROUND      = 0x90 #
ACK_ENABLE      = 0xD5 #
ACK_DISABLE     = 0xD6 #
READ_BD_BYTE    = 0xE4 # Read from memory with BDM in map.
READ_BD_WORD    = 0xEC #
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
GO_UNTIL        = 0x0C #
GO              = 0x08
TRACE1          = 0x10

TAGGO           = 0x18

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

def slicer(iteratable, sliceLength, resultType = None):
    if resultType is None:
        resultType = type(iteratable)
    length = len(iteratable)
    return [resultType(iteratable[i : i + sliceLength]) for i in range(0, length, sliceLength)]


def hexDump(arr):
    return ' '.join([("0x%02x" % x) for x in arr])

class CommunicationError(Exception): pass


class BDMBase(object):
    """ .. class:: BDM

        BDM Communication base class.
    """

    __metaclass__= abc.ABCMeta
    DEVICE_NAME = None
    VARIABLE_BUS_FREQUENCY = False

    def __init__(self, *args, **kwargs):
        self.logger = Logger()
        super(BDMBase,self).__init__(*args, **kwargs)
        self.bdmModule = Bdm(self)

    @abstractmethod
    def reset(self):
        self.logger.debug("Resetting Target.")

    def targetGo(self):
        """ ..  py:method:: targetGo(self)

               Go to user program.  If enabled, ACK will occur when leaving active background mode.
        """
        self.logger.debug("GO")
        self.__writeCommand__(GO)

    def targetGoUntil(self):
        """ ..  py:method:: targetGoUntil(self)

               Go to user program. If enabled, ACK will occur upon returning to active background mode.
        """
        self.logger.debug("GO_UNTIL")
        self.__writeCommand__(GO_UNTIL)

    def targetTagGo(self):
        """ ..  py:method:: targetTagGo(self)

               Enable tagging and go to user program. There is no ACK pulse related to this command.
        """
        self.logger.debug("TAGGO")
        self.__writeCommand__(TAGGO)

    def targetHalt(self):
        """ ..  py:method:: targetHalt(self)

               Enter background mode if firmware enabled.
        """
        self.logger.debug("BACKGROUND")
        self.__writeCommand__(BACKGROUND)

    def targetAckEnable(self):
        """ ..  py:method:: targetAckEnable(self)

               Enable Handshake. Issues an ACK pulse after the command is executed.
        """
        self.logger.debug("ACK_ENABLE")
        self.__writeCommand__(ACK_ENABLE)

    def targetAckDisable(self):
        """ ..  py:method:: targetAckDisable(self)

               Disable Handshake. This command does not issue an ACK pulse.
        """
        self.logger.debug("ACK_DISABLE")
        self.__writeCommand__(ACK_DISABLE)

    def readBDWord(self, addr):
        """ ..  py:method:: readBDWord(addr)

                Read from memory with BDM in map.

                :param addr: 16-bit address to read from.
                :type addr: integer
                :rtype: integer
        """
        self.logger.debug("READ_BD_WORD[0x%04x]" % addr)
        data = self.__readWord__(READ_BD_WORD, addr)
        self.logger.debug("RESULT: 0x%04x" % data)
        return data

    def readWord(self, addr):
        """ ..  py:method::
        """
        self.logger.debug("READ_WORD[0x%04x]" % addr)
        data = self.__readWord__(READ_WORD, addr)
        self.logger.debug("RESULT: 0x%04x" % data)
        return data

    def readBDByte(self, addr):
        """ ..  py:method::
        """
        self.logger.debug("READ_BD_BYTE[0x%04x]" % addr)
        data = self.__readCommand__(READ_BD_BYTE, 1, addr)[0]
        self.logger.debug("RESULT: 0x%02x" % data)
        return data

    def readByte(self, addr):
        """ ..  py:method::
        """
        self.logger.debug("READ_BYTE[0x%04x]" % addr)
        data = self.__readCommand__(READ_BYTE, 1, addr)[0]
        self.logger.debug("RESULT: 0x%02x" % data)
        return data

    def writeBDWord(self, addr, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_BD_WORD[0x%04x]=0x%04x" % (addr, data))
        self.__writeWord__(WRITE_BD_WORD, addr, data)

    def writeBDByte(self, addr, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_BD_BYTE[0x%04x]=0x%02x" % (addr, data))
        self.__writeByte__(WRITE_BD_BYTE,addr, data)

    def writeByte(self, addr, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_BYTE[0x%04x]=0x%02x" % (addr, data))
        self.__writeByte__(WRITE_BYTE, addr, data)

    def writeWord(self, addr, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_WORD[0x%04x]=0x%04x" % (addr, data))
        self.__writeWord__(WRITE_WORD, addr, data)

    def readNext(self):
        """ ..  py:method::
        """
        self.logger.debug("READ_NEXT")
        return self.__readWord__(READ_NEXT)

    def writeNext(self,data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_NEXT[0x%04x]" % data)
        self.__writeWord__(WRITE_NEXT, data)

    def readPC(self):
        """ ..  py:method::
        """
        self.logger.debug("READ_PC")
        return self.__readWord__(READ_PC)

    def readD(self):
        """ ..  py:method::
        """
        self.logger.debug("READ_D")
        return self.__readWord__(READ_D)

    def readX(self):
        """ ..  py:method::
        """
        self.logger.debug("READ_X")
        return self.__readWord__(READ_X)

    def readY(self):
        """ ..  py:method::
        """
        self.logger.debug("READ_Y")
        return self.__readWord__(READ_Y)

    def readSP(self):
        """ ..  py:method::
        """
        self.logger.debug("READ_SP")
        return self.__readWord__(READ_SP)

    def writePC(self, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_PC[0x{0:04x]".format(data))
        self.__writeWord__(WRITE_PC, data)

    def writeD(self, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_D[0x{0:04x]".format(data))
        self.__writeWord__(WRITE_D, data)

    def writeX(self, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_X[0x%04x]", data)
        self.__writeWord__(WRITE_X, data)

    def writeY(self, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_Y[0x%04x]", data)
        self.__writeWord__(WRITE_Y, data)

    def writeSP(self, data):
        """ ..  py:method::
        """
        self.logger.debug("WRITE_SP[0x%04x]", data)
        self.__writeWord__(WRITE_SP, data)

##
## Convenience Methods.
##
    def readCCR(self):
        """ ..  py:method::
        """
        return self.bdmModule.bdmccr

    def writeCCR(self, value):
        """ ..  py:method::
        """
        self.bdmModule.bdmccr = value

    def getPartID(self):
        """ ..  py:method::
        """
        """ NB: the 'classic' HC12 derivates don't have PartID-Registers! """
        return self.readWord(0x001a)

    def getMemorySizes(self):
        """ ..  py:method::
        """
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
        """ ..  py:method::
        """
        if length == 0:
            return None
        loops = length / self.MAX_READ_PAYLOAD
        bytesRemaining = length % self.MAX_READ_PAYLOAD
        offset = addr
        result = bytearray()
        for l in range(loops):
            self.logger.debug("Reading %u bytes starting @ 0x%04x." % (self.MAX_READ_PAYLOAD, offset))
            data = self.__readArea__(offset, self.MAX_READ_PAYLOAD)
            self.logger.debug("[%s]" % hexDump(data))
            result.extend(data)
            offset += self.MAX_READ_PAYLOAD
        if bytesRemaining:
            self.logger.debug("Reading %u bytes starting @ 0x%04x." % (bytesRemaining, offset))
            data = self.__readArea__(offset,bytesRemaining)
            self.logger.debug("[%s]" % hexDump(data))
            result.extend(data)
        return result

    def fillArea(self, addr, value, length):
        """ ..  py:method::
        """
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
        """ ..  py:method::
        """
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
            dslice = data[dataOffsetFrom : dataOffsetTo]
            self.logger.debug("[%s]" % hexDump(dslice))
            self.__writeArea__(addrOffset, self.MAX_WRITE_PAYLOAD, dslice)
            addrOffset += self.MAX_WRITE_PAYLOAD
            dataOffsetFrom = dataOffsetTo
            dataOffsetTo = dataOffsetFrom + self.MAX_WRITE_PAYLOAD
        if bytesRemaining:
            self.logger.debug('Writing %u bytes starting @ 0x%04x.' % (bytesRemaining, addrOffset))
            dslice = data[dataOffsetFrom: dataOffsetFrom + bytesRemaining]
            self.logger.debug("[%s]" % hexDump(dslice))
            self.__writeArea__(addrOffset, bytesRemaining, dslice)

    def getPPage(self):
        """ ..  py:method::
        """
        return self.readBDByte(PPAGE)

    def setPPage(self, value):
        """ ..  py:method::
        """
        self.writeBDByte(PPAGE, value)

    def getVector(self, vectorNumber):
        """ ..  py:method::
        """
        addr = MEMORY_HIGH - (2 * vectorNumber) - 1
        content = self.readWord(addr)
        return content

    def getResetVector(self):
        """ ..  py:method::
        """
        return self.getVector(RESET_VECTOR)

    def getCMFVector(self):
        """ ..  py:method::
        """
        return self.getVector(CMF_VECTOR)

    def getCOPVector(self):
        """ ..  py:method::
        """
        return self.getVector(COP_VECTOR)

    def getTrapVector(self):
        """ ..  py:method::
        """
        return self.getVector(TRAP_VECTOR)

    def getSWIVector(self):
        """ ..  py:method::
        """
        return self.getVector(SWI_VECTOR)

    def getXIRQVector(self):
        """ ..  py:method::
        """
        return self.getVector(XIRQ_VECTOR)

    def getIRQVector(self):
        """ ..  py:method::
        """
        return self.getVector(IRQ_VECTOR)

