#!/usr/bin/env python
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

from pyBDM.module import Module


PEAR        = 0x000a
NOACCE  = 0x80
PIPOE   = 0x20
NECLK   = 0x10
LSTRE   = 0x08
RDWE    = 0x04

MODE        = 0x000b
MODC    = 0x80
MODB    = 0x40
MODA    = 0x20
IVIS    = 0x08
EMK     = 0x02
EME     = 0x01


PUCR        = 0x000c
PUPKE   = 0x80
PUPEE   = 0x10
PUPBE   = 0x02
PUPAE   = 0x01


RDRIV       = 0x000d
RDPK    = 0x80
RDPE    = 0x10
RDPB    = 0x02
RDPA    = 0x01


EBICTL      = 0x000e
ESTR    = 0x01


IRQCR       = 0x001e
IRQE    = 0x80
IRQEN   = 0x40


class MEBI(Module):
    __REGISTERS8__ = (
        ('pear',    PEAR),
        ('mode',    MODE),
        ('pucr',    PUCR),
        ('rdriv',   RDRIV),
        ('ebictl',  EBICTL),
        ('irqcr',   IRQCR),
    )

    def _getModeAsString(self):
        return {
            0b00000000: "Special Single Chip",
            0b00101011: "Emulation Expanded Narrow",
            0b01001000: "Special Test",
            0b01101011: "Emulation Expanded Wide",
            0b10000000: "Normal Single Chip",
            0b10100000: "Normal Expanded Narrow",
            0b11000000: "Peripheral",
            0b11100000: "Normal Expanded Wide",
        }.get(self.mode, 'Unknown')

    modeAsString = property(_getModeAsString)


