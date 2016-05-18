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

from pyBDM.Module import Module


##
## Registers.
##
DBGC1           = 0x0020
DBGEN   = 0x80
ARM     = 0x40
TRGSEL  = 0x20
BEGIN   = 0x10
DBGBRK  = 0x08
CAPMOD1 = 0x02
CAPMOD0 = 0x01

DBGSC           = 0x0021
AF      = 0x80
BF      = 0x40
CF      = 0x20
TRG3    = 0x08
TRG2    = 0x04
TRG1    = 0x02
TRG0    = 0x01

DBGTBH          = 0x0022

DBGTBL          = 0x0023

DBGCNT          = 0x0024
TBF     = 0x80
CNT5    = 0x20
CNT4    = 0x10
CNT3    = 0x08
CNT2    = 0x04
CNT1    = 0x02
CNT0    = 0x01

DBGCCX          = 0x0025
PAGSEL1 = 0x80
PAGSEL0 = 0x40
EXTCMP5 = 0x20
EXTCMP4 = 0x10
EXTCMP3 = 0x08
EXTCMP2 = 0x04
EXTCMP1 = 0x02
EXTCMP0 = 0x01

DBGCCH          = 0x0026

DBGCCL          = 0x0027

DBGC2           = 0x0028    # BKPCT0
BKABEN  = 0x80
FULL    = 0x40
BDM     = 0x20
TAGAB   = 0x10
BKCEN   = 0x08
TAGC    = 0x04
RWCEN   = 0x02
RWC     = 0x01

DBGC3           = 0x0029    # BKPCT1
BKAMBH  = 0x80
BKAMBL  = 0x40
BKBMBH  = 0x20
BKBMBL  = 0x10
RWAEN   = 0x08
RWA     = 0x04
RWBEN   = 0x02
RWB     = 0x01

DBGCAX          = 0x002A    # BKP0X
# s. DBGCCX

DBGCAH          = 0x002B    # BKP0H

DBGCAL          = 0x002C    # BKP0L

DBGCBX          = 0x002D    # BKP1X
# s. DBGCCX

DBGCBH          = 0x002E    # BKP1H

DBGCBL          = 0x002F    # BKP1L


## Capture Modes.
CAPMOD_NORMAL   = 0x00
CAPMOD_LOOP1    = 0x01
CAPMOD_DETAIL   = 0x02
CAPMOD_PROFILE  = 0x03

# Triggers
TRIGGER_A_MATCH             = 0x01
TRIGGER_B_MATCH             = 0x02
TRIGGER_COMP_C_MATCH        = 0x03
TRIGGER_A_ONLY              = 0x04
TRIGGER_A_OR_B              = 0x05
TRIGGER_A_THEN_B            = 0x06
TRIGGER_EVENT_ONLY_B        = 0x07
TRIGGER_A_THEN_EVENT_ONLY_B = 0x08
TRIGGER_A_AND_B             = 0x09
TRIGGER_A_AND_NOT_B         = 0x0a
TRIGGER_INSIDE_RANGE        = 0x0b
TRIGGER_OUTSIDE_RANGE       = 0x0c

import random

class Port(object):
    def readByte(self, addr):
        value =  random.randint(0, 0xff)
        return value

    def writeByte(self, addr, value):
        pass


"""
0000 A only
0001 A or B
0010 A then B
0011 Event only B
0100 A then event only B
0101 A and B (full mode)
0110 A and Not B (full mode)
0111 Inside range
1000 Outside range
1001
?
1111
Reserved
(Defaults to A only)
"""

class Dbg(Module):
    __REGISTERS8__ = (
        ('dbgc1',  DBGC1),
        ('dbgsc',  DBGSC),
        #('dbgtbh', DBGTBH),
        #('dbgtbl', DBGTBL),
        ('dbgcnt', DBGCNT),
        ('dbgccx', DBGCCX),
        #('dbgcch', DBGCCH),
        #('dbgccl', DBGCCL),
        ('dbgc2',  DBGC2),
        ('dbgc3',  DBGC3),
        ('dbgcax', DBGCAX),
        #('dbgcah', DBGCAH),
        #('dbgcal', DBGCAL),
        ('dbgcbx', DBGCBX),
        #('dbgcbh', DBGCBH),
        #('dbgcbl', DBGCBL),
    )
    __REGISTERS16 = (
        ('dbgtb', DBGTBH),
        ('dbgcc', DBGCCH),
        ('dbgca', DBGCAH),
        ('dbgcb', DBGCBH)
    )

    def enableBkpMode(self):
        self.setRegisterBits(self.dbgc2, BKABEN)

    def enableDbgMode(self):
        self.clearRegisterBits(self.dbgc2, BKABEN)
        self.setRegisterBits(self.dbgc1, DBGEN)

    def armDebugger(self):
        self.setRegisterBits(self.dbgc1, ARM)

    def unarmDebugger(self):
        self.clearRegisterBits(self.dbgc1, ARM)

    def selectTrigger(self, trigger, triggerBefore = True):
        triggerPoint = BEFORE if triggerBefore else 0x00

    def enableDebugBreakPoint(self):
        self.setRegisterBits(self.dbgc1, DBGBRK)

    def disableDebugBreakPoint(self):
        self.clearRegisterBits(self.dbgc1, DBGBRK)

    def setCaptureMode(captureMode):
        self.setRegisterBits(self.dbgc1, captureMode)

