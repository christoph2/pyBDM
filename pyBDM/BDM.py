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
import abc

abstractmethod=abc.abstractmethod

from collections import namedtuple
MemorySizes=namedtuple('MemorySizes','regSpace eepSpace ramSpace allocRomSpace')

class Device(object):
    __metaclass__=abc.ABCMeta
    DEVICE_NAME=None

    @abstractmethod
    def reset(self):                    pass
    @abstractmethod
    def targetGo(self):                 pass
    @abstractmethod
    def targetTagGo(self):              pass
    @abstractmethod
    def targetHalt(self):               pass
    @abstractmethod
    def targetTrace(self):              pass

    @abstractmethod
    def readBDWord(self,addr):          pass
    @abstractmethod
    def readWord(self):                 pass
    @abstractmethod
    def writeBDWord(self,addr,data):    pass
    @abstractmethod
    def writeWord(self,addr,data):      pass
    @abstractmethod
    def readNext(self):                 pass
    @abstractmethod
    def writeNext(self,data):           pass
    @abstractmethod
    def readPC(self):                   pass
    @abstractmethod
    def readD(self):                    pass
    @abstractmethod
    def readX(self):                    pass
    @abstractmethod
    def readY(self):                    pass
    @abstractmethod
    def readSP(self):                   pass
    @abstractmethod
    def readCCR(self):                  pass

    @abstractmethod
    def writePC(self,data):             pass
    @abstractmethod
    def writeD(self,data):              pass
    @abstractmethod
    def writeX(self,data):              pass
    @abstractmethod
    def writeY(self,data):              pass
    @abstractmethod
    def writeSP(self,data):             pass
    @abstractmethod
    def writeCCR(self,data):            pass
    @abstractmethod
    def close(self):                    pass

    def getPartID(self):
        """Note the 'classic' HC12-Derivates don't have PartID-Registers! """
        return self.readWord(0x001a)

    def getMemorySizes(self): #todo: Zerlegen in RAM/FLASH/EEPROM!!!
        """Note the 'classic' HC12-Derivates don't have MEMSIZE-Registers! """

        EEP_MAP={0: 0, 1: 2*1024, 2: 4*1024, 3: 8*1024}
        RAM_MAP={0: 2*1024, 1: 4*1024, 2: 6*1024, 3: 8*1024, 4: 10*1024, 5: 12*1024, 6: 14*1024, 7: 16*1024}
        ROM_MAP={0: 0*1024, 1: 16*1024, 2: 48*1024, 3: 64*1024}
        memSize=self.readWord(0x001c)
        regSpace=(memSize & 0x8000) >> 15
        if regSpace==1:
            regSpace=2
        else:
            regSpace=1
        regSpace*=1024

        eepSpace=EEP_MAP[(memSize & 0x3000) >> 12]
        ramSpace=RAM_MAP[(memSize & 0x0700) >> 8]
        allocRomSpace=ROM_MAP[(memSize & 0x00C0) >> 6]
        pageSpace=(memSize & 0x0003)

        return MemorySizes(regSpace,eepSpace,ramSpace,allocRomSpace)
# def getBDMStatus(self)

    def writeArea(self,addr,data):
        pass
