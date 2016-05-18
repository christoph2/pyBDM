#!/usr/bin/env python
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

from pyBDM.module import Module

INITRM      = 0x0010
RAM15   = 0x80
RAM14   = 0x40
RAM13   = 0x20
RAM12   = 0x10
RAM11   = 0x08
RAMHAL  = 0x01

INITRG      = 0x0011
REG14   = 0x40
REG13   = 0x20
REG12   = 0x10
REG11   = 0x08

INITEE      = 0x0012
EE15    = 0x80
EE14    = 0x40
EE13    = 0x20
EE12    = 0x10
EE11    = 0x08
EEON    = 0x01

MISC        = 0x0013
EXSTR1  = 0x08
EXSTR0  = 0x04
ROMHM   = 0x02
ROMON   = 0x01

MEMSIZ0     = 0x001C
REG_SW0 = 0x80
EEP_SW1 = 0x20
EEP_SW0 = 0x10
RAM_SW2 = 0x04
RAM_SW1 = 0x02
RAM_SW0 = 0x01

MEMSIZ1     = 0x001D
ROM_SW1 = 0x80
ROM_SW0 = 0x40
PAG_SW1 = 0x02
PAG_SW0 = 0x01

PPAGE       = 0x0030
PIX5    = 0x20
PIX4    = 0x10
PIX3    = 0x08
PIX2    = 0x04
PIX1    = 0x02
PIX0    = 0x01


class MMC(Module):
    __REGISTERS8__ = (
        ('initrm',  INITRM),
        ('initrg',  INITRG),
        ('initee',  INITEE),
        ('misc',    MISC),
        ('memsiz0', MEMSIZ0),
        ('memsiz1', MEMSIZ1),
        ('ppage',   PPAGE),
    )
