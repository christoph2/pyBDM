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

from pyBDM.module import Module


##
##  Flash Registers.
##
FCLKDIV             =     0x0100
# FCLKDIV-Bits.
FDIVLD      =     0x80
PRDIV8      =     0x40
FDIV5       =     0x20
FDIV4       =     0x10
FDIV3       =     0x08
FDIV2       =     0x04
FDIV1       =     0x02
FDIV0       =     0x01


FSEC                =     0x0101
# FSEC-Bits.
KEYEN1      =     0x80
KEYEN0      =     0x40
NV5         =     0x20
NV4         =     0x10
NV3         =     0x08
NV2         =     0x04
SEC1        =     0x02
SEC0        =     0x01


FTSTMOD             =     0x0102
# FTSTMOD-Bits.
WRALL       =     0x10


FCNFG               =     0x0103
# FCNFG-Bits.
CBEIE       =     0x80
CCIE        =     0x40
KEYACC      =     0x20
BKSEL1      =     0x02
BKSEL0      =     0x01


FPROT               =     0x0104
# FPROT-Bits.
FPOPEN      =     0x80
NV6         =     0x40
FPHDIS      =     0x20
FPHS1       =     0x10
FPHS0       =     0x08
FPLDIS      =     0x04
FPLS1       =     0x02
FPLS0       =     0x01


FSTAT               =     0x0105
# FSTAT-Bits.
CBEIF       =     0x80
CCIF        =     0x40
PVIOL       =     0x20
ACCERR      =     0x10
BLANK       =     0x04


FCMD                =     0x0106
# FCMD-Bits.
CMDB6       =     0x40
CMDB5       =     0x20
CMDB2       =     0x04
CMDB0       =     0x01


FADDR               =     0x0108
FDATA               =     0x011a

"""
$FF0D Flash 0
$FF0C Flash 1
$FF0B Flash 2
$FF0A Flash 3
"""

##
##  Flash Commands.
##
ERASE_VERIFY    = 0x05
PROGRAM         = 0x20
SECTOR_ERASE    = 0x40
MASS_ERASE      = 0x41


class Flash(Module):
    __REGISTERS8__ = (
        ('fclkdiv', FCLKDIV),
        ('fsec',    FSEC),
        ('ftstmod', FTSTMOD),
        ('fcnfg',   FCNFG),
        ('fprot',   FPROT),
        ('fstat',   FSTAT),
        ('fcmd',    FCMD),
    )

    __REGISTERS16__ = (
        ('faddr',   FADDR),
        ('fdata',   FDATA),
    )

    LRS_512     = 0x00
    LRS_1K      = 0x01
    LRS_2K      = 0x02
    LRS_4K      = 0x03

    HRS_2K      = 0x00
    HRS_4K      = 0x01
    HRS_8K      = 0x02
    HRS_16K     = 0x03

    def selectBank(self, bank):
        tmp = self.fcnfg & (CBEIE | CCIE | KEYACC)
        tmp |= bank
        self.fcnfg = tmp

    def clearErrors(self, bank = None):
        if bank:
            self.selectBank(bank)
        self.fstat = (PVIOL | ACCERR)

    def secured(self):
        return (self.fsec & 0x03) != 0x02

    def keyAccess(self):
        return (self.fsec & 0xc0) == 0x80

    def errors(self):
        return self.fstat & (PVIOL | ACCERR)

    # protectAll()
    def protect(self, lower, lowerRangeSize, upper, upperRangeSize):
        tmp = self.fprot

        fphdis = 0x00 if upper else FPHDIS
        fpldis = 0x00 if lower else FPLDIS

        #tmp = ()
        self.fprot = tmp

        self._flashCommand(PROGRAM, 0xFF0E, 0xFF00)

    def unprotect(self, lower, upper):
        tmp = self.fprot

        self.fprot = tmp

    def _waitReady(self):
        while (self.fstat & CBEIF) == 0x00:
            pass    ## TODO: timeout!

    def _waitCompletion(self):
        while (self.fstat & CCIF) == 0x00:
            pass    ## TODO: timeout!

    def _flashCommand(self, command, addr, data):
        print("FCnfg: %#x" % self.fcnfg)
        print("Fprot: %#x" % self.fprot)
        print("Fstat: %#x %#x" % (self.fstat, self.errors()))
        self._waitReady()
        ## TODO: Check for Address alignment!!!
        self._port.writeWord(addr, data)

        print("Fstat: %#x %#x" % (self.fstat, self.errors()))
        self.fcmd = command
        print("Fstat: %#x %#x" % (self.fstat, self.errors()))
        self.fstat = CBEIF  # Start command.
        print("Fstat: %#x %#x" % (self.fstat, self.errors()))
        errors = self.errors()
        if errors:
            # TODO: Vernünftiges Errorhandling!!!
            print("Errors while flashing: %#x" % errors)
        else:
            print("Fstat: %#x %#x" % (self.fstat, self.errors()))
            self._waitCompletion()

    def eraseBlock(self, block):
        self._flashCommand(MASS_ERASE, 0x8000, 0xaffe)

    def eraseAll(self):
        self.writeAll()
        self.fcnfg = 0x00
        self.fprot = FPOPEN | FPHDIS | FPLDIS
        self._flashCommand(MASS_ERASE, 0xc000, 0xaffe)


    def test(self, addr, data):
        self._flashCommand(PROGRAM, addr, data)

    def writeAll(self):
        self.ftstmod = WRALL

    #def protect(self):
    #    self.fprot = 0x00

    def unsecure(self):
        self.eraseAll()
        self.fcnfg = 0x00
        self.writeAll()
        self.fprot = FPOPEN | FPHDIS | FPLDIS
        self._port.writeWord(0xc000, 0xaffe)
        self.fcmd = MASS_ERASE
        self.fstat = CBEIF
        while (self.fstat & CCIF) == 0x00:
            pass

    def lockUnsecure(self):
        """
            a. Write FCLKDIV register to set the Flash clock for proper timing.
            b. Write $00 to FCNFG register to select Flash block 0.
            c. Disable Flash protection by writing the FPROT register.
            d. Write $FFFE to address $FF0E
            e. Write Program command($20) to FCMD register.
            f. Clear CBIEF (bit 7) it FSTAT register.
            g. Wait until Flash CCIF flag is set to 1 again.
        """
        self.fcnfg = 0x00
        self.fprot = FPOPEN | FPHDIS | FPLDIS
        self._port.writeWord(0xFF0E, 0xFFFE)
        self.fcmd = PROGRAM
        self.fstat = CBEIF
        while (self.fstat & CCIF) == 0x00:
            pass
        print("Finished.")

"""
FTS256:
4 Block a 4 Pages

Block #     Page
================
0           $3c
            $3d
            $3e
            $3f

1           $38
            $39
            $3a
            $3b

2           $34
            $35
            $36
            $37

3           $30
            $31
            $32
            $33
"""

"""

static void S12Fls_PageSelect(uint8 page)
{
    S12FLS_REG8(FCNFG)    &= ~(FLS_NUM_BANKS - 1);
    S12FLS_REG8(FCNFG)    |= ((page - FLS_PPAGE_OFFSET) >> 2) ^ (FLS_NUM_BANKS - 1);
    S12MMC_REG8(PPAGE)     = page;
}


static void S12Fls_ClearPendingErrors(void)
{
    uint8 idx;

    for (idx = (uint8)0x00; idx < FLS_NUM_BANKS; ++idx) {
        S12FLS_REG8(FCNFG)    &= ~(FLS_NUM_BANKS - 1);
        S12FLS_REG8(FCNFG)    |= idx;
        S12FLS_REG8(FSTAT)     = (PVIOL | ACCERR);
    }
}


"""
