#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '0.1.0'

__copyright__ = \
    """
    pyBDM - Library for the Motorola/Freescale Background Debugging Mode.

   (C) 2010-2014 by Christoph Schueler <github.com/Christoph2,
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

from collections import namedtuple
import functools
import itertools
import logging
from optparse import OptionParser, make_option
import re
import os
import sys
import time
from pyBDM.compod12 import ComPod12
from pyBDM.KevinRo import KevinRoBDM12


PODs = {'compod12': ComPod12, 'kevinro': KevinRoBDM12}

VALID_BYTE_COUNTS = (0x01, 0x02, 0x04, 0x08)

arrayToWord = lambda arr: functools.reduce(lambda v, accum: (v * 256) + accum, arr)

def unpack(*args):
    return args


def slicer(iteratable, sliceLength, resultType = None):
    if resultType is None:
        resultType = type(iteratable)
    length = len(iteratable)
    return [resultType(iteratable[i : i + sliceLength]) for i in range(0, length, sliceLength)]

isprintable = lambda ch: 0x1F < ch < 127

class Dumper(object):
    def __init__(self, fout = sys.stdout, numAddressBits = 24):
        self._fout = fout
        self._rolloverMask = 2 ** numAddressBits
        self._nibbles = numAddressBits >> 2
        self._addressMask = "%%0%ux " % self._nibbles

    def dumpRow(self, row):
        pass

class CanonicalDumper(Dumper):
    LINE_LENGTH = 0x10

    def printHexBytes(self, row):
        print '|%s|' % ('%s' * len(row) % unpack(*[isprintable(x) and chr(x) or '.' for x in row]))

    def dumpRow(self, row, startAddr):
        startPos = 0
        print self._addressMask % ((startPos + startAddr) % self._rolloverMask),
        print '%02x ' * len(row) % unpack(*row),
        self.printHexBytes(row)


def dumpData(dumper, data, offset = 0):
    end = len(data)
    startPos = 0x00
    #startPos = startAddr
    endPos = 0x10
    while endPos < end:
        row = data[startPos : endPos]
        dumper.dumpRow(row, startPos)
        startPos = endPos
        endPos = endPos + 0x10
    row = data[startPos : endPos]
    dumper.dumpRow(row, startPos)


class OneByteOctalDumper(Dumper):
    def dumpRow(self, row, startAddr):
        startPos = 0
        print self._addressMask % ((startPos + startAddr) % self._rolloverMask),
        print '%03o ' * len(row) % unpack(*row)

class TwoByteOctalDumper(Dumper): pass

class OneByteCharDumper(Dumper): pass

class TwoByteDecimalDumper(Dumper): pass

class TwoByteHexDumper(Dumper): pass

class FormattedDumper(Dumper): pass


###
###
###

BASE = r'C:\projekte\csProjects\pyBDM\pyBDM\S12\programmer'
START_OF_RAM = 0x1000

def formatBin(image):
    return ' '.join(["0x%02x" % b for b in image])

class Loader(object):

    def __init__ (self, pod):
        self.pod = pod
        self.prolog()

    def prolog(self):
        self.pod.reset()
        d = self.pod.getPODVersion()
        d = self.pod.readBDByte(0xff01)
        d = self.pod.readByte(0x000b)

        d = self.pod.readBDByte(0xff01)
        self.pod.writeBDByte(0xff01, 0xc4)
        d = self.pod.readByte(0x0030)

        d = self.pod.readBDByte(0xff01)



        """
        RP_MJ_WRITE     Serial0 SUCCESS Length 3: E8 FF FE      ; READ_WORD
        RP_MJ_READ      Serial0 SUCCESS Length 2: 4B D9

        RP_MJ_WRITE     Serial0 SUCCESS Length 1: 63            ; READ_PC
        RP_MJ_READ      Serial0 SUCCESS Length 2: 4A 4D

        RP_MJ_WRITE     Serial0 SUCCESS Length 1: 64            ; READ_D
        RP_MJ_READ      Serial0 SUCCESS Length 2: 00 00

        RP_MJ_WRITE     Serial0 SUCCESS Length 1: 65            ; READ_X
        RP_MJ_READ      Serial0 SUCCESS Length 2: 00 00

        RP_MJ_WRITE     Serial0 SUCCESS Length 1: 66            ; READ_Y
        RP_MJ_READ      Serial0 SUCCESS Length 2: 00 00

        RP_MJ_WRITE     Serial0 SUCCESS Length 1: 67            ; READ_SP
        RP_MJ_READ      Serial0 SUCCESS Length 2: 00 00

        RP_MJ_WRITE     Serial0 SUCCESS Length 3: E4 FF 06      ; READ_BD_BYTE
        RP_MJ_READ      Serial0 SUCCESS Length 1: D8

        RP_MJ_WRITE     Serial0 SUCCESS Length 3: 43 4B D9      ; WRITE_PC
        RP_MJ_READ      Serial0 SUCCESS Length 1: BC

        RP_MJ_WRITE     Serial0 SUCCESS Length 3: 44 00 00      ; WRITE_D
        RP_MJ_READ      Serial0 SUCCESS Length 1: BB

        RP_MJ_WRITE     Serial0 SUCCESS Length 3: 45 00 00      ; WRITE_X
        RP_MJ_READ      Serial0 SUCCESS Length 1: BA

        RP_MJ_WRITE     Serial0 SUCCESS Length 3: 46 00 00      ; WRITE_Y
        RP_MJ_READ      Serial0 SUCCESS Length 1: B9

        RP_MJ_WRITE     Serial0 SUCCESS Length 3: 47 00 00      ; WRITE_SP
        RP_MJ_READ      Serial0 SUCCESS Length 1: B8

        RP_MJ_WRITE     Serial0 SUCCESS Length 4: C4 FF 06 D8   ; WRITE_BD_BYTE
        RP_MJ_READ      Serial0 SUCCESS Length 1: 3B

        RP_MJ_WRITE     Serial0 SUCCESS Length 3: E0 00 0B      ; READ_BYTE
        RP_MJ_READ      Serial0 SUCCESS Length 1: 00

        RP_MJ_WRITE     Serial0 SUCCESS Length 4: 83 00 1A 02   ; READ_AREA
        RP_MJ_READ      Serial0 SUCCESS Length 2: 00 12
        """

    def loadFlasherImage(self):
        flashImage = bytearray(open(os.path.join(BASE, 'flash.bin'), 'rb').read())
        print "Loading Flasher Image..."
        #print formatBin(flashImage)
        self.pod.writeArea(START_OF_RAM, flashImage)
        print "Done."
        readBack = self.pod.readArea(START_OF_RAM, len(flashImage))
        dumpData(CanonicalDumper(), readBack)

        #print "PC: %#x" % (self.pod.bdmModule)

        #readBack = self.pod.readArea(START_OF_RAM, len(flashImage))
        #dumpData(CanonicalDumper(), readBack)
        #assert(flashImage == readBack)
###
###
###

import types
from pyBDM.BDM import hexDump

def dumpa(arr):
    return ' '.join([("0x%02x" % ord(x)) for x in arr])

def injectReader(pod):  # Example for DI!!!
    reader = pod.port.read
    #print reader
    def read(self, length):
        data = reader(length)
        print "*** READ[%u]: '%s'." % (length, dumpa(data))
        return data
    #print help(types.MethodType)
    print
    pod.port.read = types.MethodType(read, pod)



def main():
    options = []
    args = []

    usage = """%s bdm-pod options

    bdm-pod: [%s]
    """ \
        % (os.path.split(sys.argv[0x00])[0x01], '|'.join(PODs.keys()))

    option_list = [
        make_option("-b", help = "one-byte octal display",
                action = "store_true", dest = "oneByteOctal"),
        make_option("-c", help = "one-byte character display",
                action="store_true", dest = "oneByteChar"),
        make_option("-n", help = "interpret only length bytes of input", dest = "length", action = "store", type = "int", default = 0x100),
        make_option("-s", help = "skip offset bytes from the beginning", dest = "offset", action = "store" , type = "int", default = 0x0000),
        make_option("-p", help = "Communication port (number or name according to your operating systems conventions).", dest ="port", action = "store", default = "0")
    ]


    op = OptionParser(usage = usage, version = '%prog ' + __version__,
                      description = 'POSIX hexdump like memory dump', option_list = option_list)

    """
 -C              canonical hex+ASCII display
 -d              two-byte decimal display
 -o              two-byte octal display
 -x              two-byte hexadecimal display
 -e format       format string to be used for displaying data
 -f format_file  file that contains format strings
 -v              display without squeezing similar lines
 -V              output version information and exit
    """


    (options, args) = op.parse_args()
    if len(args) == 0x00:
        op.error('No BDM-Pod specified')
    if len(args) != 0x01:
        op.error('incorrect number of arguments')

    startAddr = options.offset
    length = options.length
    port = options.port
    if port.isdigit():
        port = int(port)

    podDevice = PODs[args[0x00].lower()]
    logger = logging.getLogger('pyBDM')
    logger.setLevel(logging.INFO)

    logger.debug('=' * 43)
    logger.debug("STARTING '%s'." % os.path.split(sys.argv[0x00])[0x01])
    logger.debug('=' * 43)
    pod = podDevice(port, 38400)
    pod.connect()

    #injectReader(pod)

    pod.reset()
    pod.targetHalt()

    pod.bdmModule.enableFirmware()
    logger.info("BDM-POD: '%s'." % pod.getPODVersion())
    logger.info('Reading %u bytes starting @ 0x%04x.' % (length, startAddr))
    startTime = time.clock()


    loader = Loader(pod)
    loader.loadFlasherImage()
    #print hex(pod.readWord(0x1000)), hex(pod.readWord(0x1002)), hex(pod.readWord(0x1004)), hex(pod.readWord(0x1006)), hex(pod.readWord(0x1008))

    data = pod.readArea(startAddr, length)
    elapsedTime = time.clock() - startTime
    logger.info("%2.2f seconds ==> %2.2f bytes/sec.", elapsedTime, length / elapsedTime)
    logger.info('Done.')
    pod.close()

    dumpData(CanonicalDumper(), data)
    #dumpData(OneByteOctalDumper(), data)


# serial.serialutil.SerialException:
## Log to file (suggested for verbosity level DEBUG).


CONTROL_CHARS = {
    0x00: 'nul', 0x01: 'soh', 0x02: 'stx', 0x03: 'etx',
    0x04: 'eot', 0x05: 'enq', 0x06: 'ack', 0x07: 'bel',
    0x08: 'bs',  0x09: 'ht',  0x0A: 'lf',  0x0B: 'vt',
    0x0C: 'ff',  0x0D: 'cr',  0x0E: 'so',  0x0F: 'si',
    0x10: 'dle', 0x11: 'dc1', 0x12: 'dc2', 0x13: 'dc3',
    0x14: 'dc4', 0x15: 'nak', 0x16: 'syn', 0x17: 'etb',
    0x18: 'can', 0x19: 'em',  0x1A: 'sub', 0x1B: 'esc',
    0x1C: 'fs',  0x1D: 'gs',  0x1E: 'rs',  0x1F: 'us',
    0xFF: 'del',
}

FMTS = \
    ("""
        "%-06.6_ao "  12/1 "%3_u "
        "\t\t" "%_p "
        "
"
    """,
     """
        "%07.7_Ax
"
        "%07.7_ax  " 8/2 "%04x " "
"
        """,
     r'"\x" 1/1 "%02x" " "', '"x" 1/1 "%02X" " "')

LITERAL = 0x00
STANDARD = 0x01


class ParameterError(Exception):
    pass


# static char *spec = ".#-+ 0123456789";


def parseFormat(format):
    expr = \
        re.compile(r'''\s*?%((?P<SIGN>[-+]?)(?P<WIDTH>\d*)\.?
        (?P<PRECISION>\d*))?(\_((?P<ADDRESS>[aA][dox])
        |(?P<CHAR>[cpu]))|(?P<STANDARD>[cdiouXxEefGg]))\s*?''',
        re.VERBOSE | re.MULTILINE
    )
    match = expr.match(format)
    if match:
        di = match.groupdict()
        address = di['ADDRESS']
        char = di['CHAR']
        standard = di['STANDARD']
        if standard:
            result = (STANDARD, format)
        elif address:
            result = '%%%s%s.%s%s' % (di.get('SIGN', ''), di['WIDTH'],
                    di['PRECISION'], address[0x01])
        elif char:
            result = '%%%s%s.%s%s' % (di.get('SIGN', ''), di['WIDTH'],
                    di['PRECISION'], 'c')
    else:
        result = (LITERAL, format)
    return result


# splitFormats


def testFormatParser():
    expr = \
        re.compile(r'''\s*?((?P<ITER_COUNT>\d+)\s*\/\s*(?P<BYTE_COUNT>\d+))?\s*"(?P<FORMAT>.*?)"'''
                   , re.VERBOSE | re.MULTILINE)

    #

    for fmt in FMTS:
        outputFormat = ''
        totalBytes = 0x00
        for match in expr.finditer(fmt):
            di = match.groupdict()
            format = di.get('FORMAT', '')
            rrr = parseFormat(format)
            print di
            if di['ITER_COUNT'] is None and di['BYTE_COUNT'] is None:

                # Single Literal.

                outputFormat += di.get('FORMAT', '')  # todo: parsen!!!
                consumesBytes = False
            elif di['BYTE_COUNT'] is None:

                                            # genügt eigentlich!

                consumesBytes = False
            else:
                consumesBytes = True
                iterCount = int(di.get('ITER_COUNT', 0x01))
                byteCount = int(di.get('BYTE_COUNT'))
                if byteCount not in VALID_BYTE_COUNTS:
                    raise ParameterError("Invalid byte count '%u' in format string."
                             % byteCount)
                totalBytes += iterCount * byteCount
        print

        # raise ParameterError("Total bytes to output == 0.")

    sys.exit(0x01)


if __name__ == '__main__':
    #testFormatParser()
    main()

