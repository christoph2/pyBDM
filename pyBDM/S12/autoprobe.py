#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.1.0"

__copyright__ = """
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

__all__ = ['autoprobe']

import PartIDs

## Log to file (suggested for verbosity level DEBUG).


MEMORY_IDs = {
    0x0: 256,
    0x1: 128,
    0x2: 64,
    0x3: 32,
    0x4: 512,
}

FAMILIES = {
    0x0: 'D',
    0x1: 'H',
    0x2: 'B',
    0x3: 'C',
    0x4: 'T',
    0x5: 'E',
    0x6: 'U',
    0x7: 'K',
    0x8: 'NE',
}

INITRM  = 0x10
INITRG  = 0x11
INITRE  = 0x12
MISC    = 0x13
PPAGE   = 0xff

FEETEST = 0xf6

BCR1    = 0xf8
BCR2    = 0xfa
BARD    = 0xfc

C0MCR0   = 0x100
C0TFLG   = 0x106

C2MCR0   = 0x200
C2TFLG   = 0x206

DERIVATES = {
    (0x20, 0x01, 0x0d) : "DG128x",
    (0x08, 0x01, 0x0f) : "A4 or B32x",
    (0x00, 0x01, 0x0f) : "D60x",
}


def probeHC12(port):
    couldBeDG128 = False

    port.logger.info("Probing for HC12 derivate.")
    initRM, initRE, misc = port.readByte(INITRM), port.readByte(INITRE), port.readByte(MISC)
    derivate = DERIVATES.get((initRM, initRE, misc),'*** UNKNOWN ***')  ## FixMe

    port.logger.info("%s" % derivate)

    if (initRM, initRE, misc)== (0x20, 0x01, 0x0d):
        ppageOld = port.readByte(PPAGE)
        port.writeByte(PPAGE,0xff)
        ppage= port.readByte(PPAGE)
        if ppage == 0x07:
            port.writeByte(PPAGE,ppageOld)
        else:
            port.logger.info("*** UNKNOWN ***")
        canMagic = (port.readByte(C2MCR0), port.readByte(C2TFLG))
        derivate = "MC68HC912D"
        if canMagic == (0x21, 0x07):
            hasCAN2 = True
        else:
            hasCAN2 = False
        if hasCAN2:
            derivate += "T"
        else:
            derivate += "G"
        derivate += "128"
        return (derivate, 'n/a')
    elif (initRM, initRE, misc)== (0x00, 0x01, 0x0f):
        "D60x"
        ## todo: testNotImplementedYet!
        return (None,'n/a')
    elif (initRM, initRE, misc)== (0x08, 0x01, 0x0f):
        port.writeByte(FEETEST,0xff)
        feetest = port.readByte(FEETEST)
        if feetest == 0xDF:
            hasFlash = True
            port.writeByte(FEETEST,0x00)
        else:
            hasFlash = False
        bdlcMagic = (port.readByte(BCR1), port.readByte(BCR2), port.readByte(BARD))
        if bdlcMagic == (0xe0, 0xc0, 0xc7):
            hasBDLC = True
        else:
            hasBDLC = False
        canMagic = (port.readByte(C0MCR0), port.readByte(C0TFLG))
        if canMagic == (0x21, 0x07):
            hasCAN = True
        else:
            hasCAN = False
        if hasFlash:
            derivate = "MC68HC912"
        else:
            derivate = "MC68HC12"
        if hasCAN:
            derivate += "BC"
        elif hasBDLC:
            if hasFlash:
                derivate += "B"
            else:
                derivate += "BE"
        else:
            assert False, "neither 'CAN' nor 'BDLC'."
        derivate += "32"
        return (derivate, 'n/a')
    else:
        ## todo: testNotImplementedYet!
        pass

def autoprobe(port):
    partID = port.getPartID()
    if partID != 0:
        '''
        familyID = (partID & 0xf000) >> 12
        memoryID = (partID & 0x0f00) >> 0x8
        maskMajor = (partID & 0x00f0) >> 0x4
        maskMinor = partID & 0x000f
        print 'PartID:  ', hex(partID)
        print 'Family:  ', FAMILIES[familyID]
        print 'Flash:    %sKB' % (MEMORY_IDs[memoryID], )
        print port.getMemorySizes()
        print 'BDM-Status: 0x%02X' % port.readBDByte(0xff01)
        '''
        id = PartIDs.IDs.get(partID, ('not supported yet', 'n/a') )  # todo: Logging!!!
        return id
    else:
        pod.logger.info(PartIDs.IDs.get(partID, 'Unknown S12-Derivate, maybe a HC12?'))
        return probeHC12(port)
