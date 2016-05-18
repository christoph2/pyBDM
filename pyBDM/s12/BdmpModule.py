#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1.0"

__copyright__ = """
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

from pyBDM.module import Module

# BDM-Status-Register.
BDMSTS          = 0xFF01
ENBDM       = 0x80
BDMACT      = 0x40
ENTAG       = 0x20
SDV         = 0x10
TRACE       = 0x08
CLKSW       = 0x04
UNSEC       = 0x02


# BDM-Instruction-Register.
BDMIST = 0xFF00
    # hardware command bits.
HF          = 0x80
DATA        = 0x40
RW          = 0x20
BKGND       = 0x10
WB          = 0x08
BDU         = 0x04
    # firmware command bits.
TTAGO       = 0x18
REGN        = 0x07


# BDM Shift Register.
BDMSHTH         = 0xFF02
BDMSHTL         = 0xFF03


# BDM Address Register.
BDMADDH         = 0xFF04
BDMADDL         = 0xFF05


# CCR Holding Register.
BDMCCR          = 0xFF06
#  Out of special single-chip reset, the BDMCCR is set to $D8 and not $D0 which is the reset value of the CCR register.
    # Condition Code Bits.
CC_S        = 0x80
CC_X        = 0x40
CC_H        = 0x20
CC_I        = 0x10
CC_N        = 0x08
CC_Z        = 0x04
CC_V        = 0x02
CC_C        = 0x01

# Internal Register Position Register.
BDMINR = 0xFF07
REG14   = 0x40
REG13   = 0x20
REG12   = 0x10
REG11   = 0x08

class Bdm(Module):
    __REGISTERS8__ = (
        ('bdmsts', BDMSTS),
        ('bdmist', BDMIST),
        ('bdmccr', BDMCCR),
        ('bdminr', BDMINR),
    )
    __REGISTERS16__ = (
        ('shifter', BDMSHTH),
        ('address', BDMADDH)
    )

    def enableFirmware(self):
        self.setRegisterBits(self.bdmsts, ENBDM)

    def disableFirmware(self):
        self.clearRegisterBits(self.bdmsts, ENBDM)

