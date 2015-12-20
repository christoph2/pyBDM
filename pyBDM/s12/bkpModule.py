#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

__copyright__ =  """
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

import logging
from pyBDM.module import Module

logger = logging.getLogger('pyBDM')

##
## Registers.
##
BKPCT0      = 0x0028
BKEN    = 0x80
BKFULL  = 0x40
BKBDM   = 0x20
BKTAG   = 0x10

BKPCT1      = 0x0029
BK0MBH  = 0x80
BK0MBL  = 0x40
BK1MBH  = 0x20
BK1MBL  = 0x10
BK0RWE  = 0x08
BK0RW   = 0x04
BK1RWE  = 0x02
BK1RW   = 0x01

BKP0X       = 0x002a
BK0V5   = 0x20
BK0V4   = 0x10
BK0V3   = 0x08
BK0V2   = 0x04
BK0V1   = 0x02
BK0V0   = 0x01

BKP0H       = 0x002b

BKP0L       = 0x002c

BKP1X       = 0x002d
BK1V5   = 0x20
BK1V4   = 0x10
BK1V3   = 0x08
BK1V2   = 0x04
BK1V1   = 0x02
BK1V0   = 0x01

BKP1H       = 0x002e

BKP1L       = 0x002f


FULL_ADDRESS_COMPARE    = 0b00
ADDRESS_RANGE_256       = 0b01
ADDRESS_RANGE_16K       = 0b11


BREAKPOINT_MODES = {
    "full": FULL_ADDRESS_COMPARE,   # The registers used for the compare are: BKP0X[5:0],BKP0H[5:0],BKP0L[7:0].
                                    # When a program page is not selected, the full address compare will be based on bits for a
                                    # 16-bit compare. The registers used for the compare are BKP0H[7:0],BKP0L[7:0].
    "256":  ADDRESS_RANGE_256,      # BKP1X:BKP1H.
    "16k":  ADDRESS_RANGE_16K       # Useful for triggering a breakpoint on any access to a particular expansion page. This
                                    # only makes sense if a program page is being accessed so that the breakpoint trigger will
                                    # occur only if BKP0X compares.
}


HIGH_AND_LOW_BYTE_COMPARE   = 0b00
HIGH_BYTE   = 0b01
LOW_BYTE    = 0b10
NO_COMPARE  = 0b11

DATA_COMPARE_MODES = {
    "full":
    "high":
    "low":
    "non":
}

READ_WRITE_MODE = {
    "rw": 0xb00,
    "r": 0xb11,
    "w": 0xb10
}

class Bkp(Module):
    __REGISTERS8__ = (
        ('bkpct0',  BKPCT0),
        ('bkpct1',  BKPCT1),
        ('bkp0x',   BKP0X),
        ('bkp0h',   BKP0H),
        ('bkp0l',   BKP0L),
        ('bkp1x',   BKP1X),
        ('bkp1h',   BKP1H),
        ('bkp1l',   BKP1L),
    )

    def enabled(self):
        return (self.bkpct0 & BKEN) == BKEN

    def enable(self):
        self.setRegisterBits(self.bkpct0, BKEN)

    def disable(self):
        self.clearRegisterBits(self.bkpct0, BKEN)

    def breakpointMode(self):
        return "full" if (self.bkpct0 & BKFULL) == BKFULL else "dual"

    def dualAddressMode(self):
        self.clearRegisterBits(self.bkpct0, BKFULL)

    def fullBreakpointMode(self):
        self.setRegisterBits(self.bkpct0, BKFULL)

    def debugMode(self):
        return "bdm" if (self.bkpct0 & BKBDM) == BKBDM else "swi"

    def bdmDebugMode(self):
        self.setRegisterBits(self.bkpct0, BKBDM)

    def swiDebugMode(self):
        self.clearRegisterBits(self.bkpct0, BKBDM)

    def onMatchBreak(self):
        return "tagged" if (self.bkpct0 & BKTAG) == BKTAG else "force"

    def breakForce(self):
        self.setRegisterBits(self.bkpct0, BKTAG)

    def breakTagged(self):
        self.clearRegisterBits(self.bkpct0, BKTAG)

    def setupDualBreakpoints(breakpoint0 = "full", rw0 = "rw", breakpoint1 = "full", rw1 = "rw"):
        if breakpoint0 not in BREAKPOINT_MODES:
            raise ValueError("breakpoint0: %s" % breakpoint0)
        if breakpoint0 not in BREAKPOINT_MODES:
            raise ValueError("breakpoint1: %s" % breakpoint1)
        value = 0x00
        value |= BREAKPOINT_MODES[breakpoint0] << 6
        value |= BREAKPOINT_MODES[breakpoint1] << 4

        # READ_WRITE_MODE
        self.bkpct1 = value

    def setupFullBreakpoint(breakpoint = "full", rw = "rw", dataBreakpoint = "non", drw = "rw"):
        if breakpoint not in BREAKPOINT_MODES:
            raise ValueError("breakpoint: %s" % breakpoint)
        if dataBreakpoint not in DATA_COMPARE_MODES:
            raise ValueError("dataBreakpoint: %s" % dataBreakpoint)
        value = 0x00
        value |= BREAKPOINT_MODES[breakpoint] << 6
        value |= DATA_COMPARE_MODES[dataBreakpoint] << 4

        # READ_WRITE_MODE
        self.bkpct1 = value

    def breakAdress0(self, address, page = None):
        if page:
            self.bkp0x = page
        lo = address & 0xff
        hi = (address & 0xff) >> 8
        self.bkp0h = hi
        self.bkp0l = lo

    def breakAdress1(self, address, page = None):
        if page:
            self.bkp1x = page
        lo = address & 0xff
        hi = (address & 0xff) >> 8
        self.bkp1h = hi
        self.bkp1l = lo


def main():
    pass

if __name__ == '__main__':
    main()

