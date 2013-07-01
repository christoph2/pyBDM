#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyBDM.Module import Module

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

class Flash(Module):
    __REGISTERS8__ = (
        ('fclkdiv', FCLKDIV),
        ('fsec',    FSEC),
        ('ftstmod', FTSTMOD),
        ('fcnfg',   FCNFG),
        ('fprot',   FPROT),
        ('fstat',   FSTAT),
        ('fcmd',    FCMD),
        ('faddr',   FADDR),
        ('fdata',   FDATA),
    )

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


