#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

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

from pyBDM.module import Module


##
##  EEPROM Registers.
##
ECLKDIV         = 0x0110
EDIVLD  = 0x80
PRDIV8  = 0x40
EDIV5   = 0x20
EDIV4   = 0x10
EDIV3   = 0x08
EDIV2   = 0x04
EDIV1   = 0x02
EDIV0   = 0x01

ECNFG           = 0x0113
CBEIE   = 0x80
CCIE    = 0x40

EPROT           = 0x0114
EPOPEN  = 0x80
NV6     = 0x40
NV5     = 0x20
NV4     = 0x10
EPDIS   = 0x08
EP2     = 0x04
EP1     = 0x02
EP0     = 0x01

ESTAT           = 0x0115
CBEIF   = 0x80
CCIF    = 0x40
PVIOL   = 0x20
ACCERR  = 0x10
BLANK   = 0x04

ECMD            = 0x0116
CMDB6   = 0x40
CMDB5   = 0x20
CMDB2   = 0x04
CMDB0   = 0x01

EADDRHI         = 0x0118

EADDRLO         = 0x0119

EDATAHI         = 0x011a

EDATALO         = 0x011b

##
##  EEPROM Commands.
##
ERASE_VERIFY    = 0x05
WORD_PROGRAM    = 0x20
SECTOR_ERASE    = 0x40
MASS_ERASE      = 0x41
SECTOR_MODIFY   = 0x60

#
# 4K EEPROM from $0000 - $0FFF.
#

class EEP(Module):
    __REGISTERS8__ = (
        ('eclkdiv', ECLKDIV),
        ('ecnfg', ECNFG),
        ('eprot', EPROT),
        ('estat', ESTAT),
        ('ecmd', ECMD),
    )

    __REGSITERS16__ = (
        ('eaddrh', EADDRHI),
        ('edatah', EDATAHI)
    )

    def clearErrors(self):
        self.estat = (PVIOL | ACCERR)

    def errors(self):
        return self.estat & (PVIOL | ACCERR)

    # protectAll()
    def protect(self, lower, lowerRangeSize, upper, upperRangeSize):
        tmp = self.fprot

        fphdis = 0x00 if upper else FPHDIS
        fpldis = 0x00 if lower else FPLDIS

        tmp = ()
        self.fprot = tmp

    def unprotect(self, lower, upper):
        tmp = self.fprot

        self.fprot = tmp

    def _waitReady(self):
        while (self.estat & CBEIF) == 0x00:
            pass    ## TODO: timeout!

    def _waitCompletion(self):
        while (self.estat & CCIF) == 0x00:
            pass    ## TODO: timeout!

    def _eepromCommand(self, command, addr, data):
        print("ECnfg: %#x" % self.ecnfg)
        print("Eprot: %#x" % self.eprot)
        print("Estat: %#x %#x" % (self.estat, self.errors()))
        self._waitReady()
        ## TODO: Check for Address alignment!!!
        self._port.writeWord(addr, data)

        print("Fstat: %#x %#x" % (self.fstat, self.errors()))
        self.ecmd = command
        print("Fstat: %#x %#x" % (self.fstat, self.errors()))
        self.estat = CBEIF  # Start command.
        print("Fstat: %#x %#x" % (self.fstat, self.errors()))
        errors = self.errors()
        if errors:
            # TODO: Vernünftiges Errorhandling!!!
            print("Errors while flashing: %#x" % errors)
        else:
            print("Fstat: %#x %#x" % (self.estat, self.errors()))
            #self._waitCompletion()

    def eraseBlock(self, block):
        self._eepromCommand(MASS_ERASE, 0x8000, 0xaffe)

    def unsecure(self):
        """
            MCU is secured.
            (Unsecuring will erase Flash and EEPROM)
            [Unsecure] [Cancel]
        """
        self.ecnfg = 0x00
        #self.ftstmod = WRALL
        self.eprot = EPOPEN | EPDIS
        self._port.writeWord(0x0f80, 0xaffe)

        print("Estat: %#x %#x" % (self.estat, self.errors()))
        self.ecmd = MASS_ERASE
        self.estat = CBEIF

        print("Estat: %#x %#x" % (self.estat, self.errors()))
        while (self.estat & CCIF) == 0x00:
            pass

