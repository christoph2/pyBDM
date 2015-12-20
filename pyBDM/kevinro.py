#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

__copyright__ = """
    pyBDM - Library for the Motorola/Freescale Background Debugging Mode.

   (C) 2010-2015 by Christoph Schueler <github.com/Christoph2,
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

import serialport

from bdm import BDMBase
#from port import Port
import time

SYNC                = 0x00
RESET_CPU           = 0x01
RESET_LOW           = 0x02
RESET_HIGH          = 0x03
ENTER_DEBUG_MODE    = 0x04 # <= v4.4
EXTENDED_COMMAND    = 0x04 # >= v4.5

# Extended Command Codes.
EXT_VERSION         = 0x00
EXT_REGDUMP         = 0x01
EXT_TRACETO         = 0x02
EXT_MEMDUMP         = 0x03
EXT_SETPARAM        = 0x04
EXT_IOCTL           = 0x05
EXT_MEMPUT          = 0x06
EXT_EXTENDEDSPEED   = 0x07

class KevinRoBDM12(BDMBase, serialport.Port):
    MAX_PAYLOAD=0xffff
    DEVICE_NAME="Kevin Ross BDM12"

    def reset(self):
        self.logger.debug("RESET")

    def connect(self):
        super(KevinRoBDM12,self).connect()
        self.port.dtrdsr=0
        self.port.rtscts=0

        self.port.setRTS(0)  # raising RTS edge needed.
        self.port.setRTS(1)
        time.sleep(0.01)
        if not self.port.getCTS():
            self.logger.error("Nothing attached. Check cable and BDM12 power.")
            raise BDM.CommunicationError()
        self.port.setRTS(0)
        time.sleep(0.01)
        if self.port.getCTS():
            self.extendedCommandsSupported=self.ctsRtsControl=True     # >= v4.5
        else:
            self.extendedCommandsSupported=self.ctsRtsControl=False    # <= v4.4
        pass

    def write(self,data):
        startTime=0
        timeSpan=0
        waitCTSToClearTimeout=self.ctsRtsControl and 0.100 or 0.02

        for ch in data:
            if self.ctsRtsControl:
                self.port.setRTS(1)
            startTime=time.time()
            startTime=time.time()
            timeSpan=-1.0
            while timeSpan<0.1:
                if self.port.getCTS():
                    break
                timeSpan=time.time()-startTime
            if not self.port.getCTS():
                self.logger.error("CTS not asserted by BDM interface. Check cable and BDM12 power.")
                raise BDM.CommunicationError()
            self.port.write(ch)
            startTime=time.time()
            timeSpan=-1.0
            while timeSpan<waitCTSToClearTimeout:
                if not self.port.getCTS():
                    break
                timeSpan=time.time()-startTime
            if self.ctsRtsControl:
                self.port.setRTS(0)
                if self.port.getCTS():
                    self.logger.debug("CTS not cleared.")

    def extendedCommand(self,code,*operands):
        pass

    def getPODVersion(self):
        if self.extendedCommandsSupported:
            data=self.extendedCommand(EXT_VERSION)
            return "%s v%02u.%02u" % (self.DEVICE_NAME,((data[0]>>4) & 0x07),(data[0] & 0x0f))
        else:
            return "%s <v4.5" % (self.DEVICE_NAME)