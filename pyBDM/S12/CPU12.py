#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__="0.1.0"

__copyright__="""
    pyBDM - Library for the Motorola/Freescale Background Debugging Mode.

   (C) 2010-2012 by Christoph Schueler <github.com/Christoph2,
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
import logging
import os
import re
import sys

from pyBDM.ComPod12 import ComPod12


##
##  Debugger/Disassambler mnemoniction: alternate Mnemonics.
##

class Register(object):
    A       = 'A'
    B       = 'B'
    D       = 'D'
    X       = 'X'
    Y       = 'Y'
    SP      = 'SP'
    CCR     = 'CCR'
    TMP2    = 'TMP2'
    TMP3    = 'TMP3'

##
## Lomnemonic Primitive Postbyte Encoding.
##
LB={
    0x00 : ("DBEQ", Register.A, '+'),
    0x01 : ("DBEQ", Register.B, '+'),
    0x04 : ("DBEQ", Register.D, '+'),
    0x05 : ("DBEQ", Register.X, '+'),
    0x06 : ("DBEQ", Register.Y, '+'),
    0x07 : ("DBEQ", Register.SP, '+'),

    0x10 : ("DBEQ", Register.A, '-'),
    0x11 : ("DBEQ", Register.B, '-'),
    0x14 : ("DBEQ", Register.D, '-'),
    0x15 : ("DBEQ", Register.X, '-'),
    0x16 : ("DBEQ", Register.Y, '-'),
    0x17 : ("DBEQ", Register.SP, '-'),

    0x20 : ("DBNE", Register.A, '+'),
    0x21 : ("DBNE", Register.B, '+'),
    0x24 : ("DBNE", Register.D, '+'),
    0x25 : ("DBNE", Register.X, '+'),
    0x26 : ("DBNE", Register.Y, '+'),
    0x27 : ("DBNE", Register.SP, '+'),

    0x30 : ("DBNE", Register.A, '-'),
    0x31 : ("DBNE", Register.B, '-'),
    0x34 : ("DBNE", Register.D, '-'),
    0x35 : ("DBNE", Register.X, '-'),
    0x36 : ("DBNE", Register.Y, '-'),
    0x37 : ("DBNE", Register.SP, '-'),

    0x40 : ("TBEQ", Register.A, '+'),
    0x41 : ("TBEQ", Register.B, '+'),
    0x44 : ("TBEQ", Register.D, '+'),
    0x45 : ("TBEQ", Register.X, '+'),
    0x46 : ("TBEQ", Register.Y, '+'),
    0x47 : ("TBEQ", Register.SP, '+'),

    0x50 : ("TBEQ", Register.A, '-'),
    0x51 : ("TBEQ", Register.B, '-'),
    0x54 : ("TBEQ", Register.D, '-'),
    0x55 : ("TBEQ", Register.X, '-'),
    0x56 : ("TBEQ", Register.Y, '-'),
    0x57 : ("TBEQ", Register.SP, '-'),

    0x60 : ("TBNE", Register.A, '+'),
    0x61 : ("TBNE", Register.B, '+'),
    0x64 : ("TBNE", Register.D, '+'),
    0x65 : ("TBNE", Register.X, '+'),
    0x66 : ("TBNE", Register.Y, '+'),
    0x67 : ("TBNE", Register.SP, '+'),

    0x70 : ("TBNE", Register.A, '-'),
    0x71 : ("TBNE", Register.B, '-'),
    0x74 : ("TBNE", Register.D, '-'),
    0x75 : ("TBNE", Register.X, '-'),
    0x76 : ("TBNE", Register.Y, '-'),
    0x77 : ("TBNE", Register.SP, '-'),

    0x80 : ("IBEQ", Register.A, '+'),
    0x81 : ("IBEQ", Register.B, '+'),
    0x84 : ("IBEQ", Register.D, '+'),
    0x85 : ("IBEQ", Register.X, '+'),
    0x86 : ("IBEQ", Register.Y, '+'),
    0x87 : ("IBEQ", Register.SP, '+'),

    0x90 : ("IBEQ", Register.A, '-'),
    0x91 : ("IBEQ", Register.B, '-'),
    0x94 : ("IBEQ", Register.D, '-'),
    0x95 : ("IBEQ", Register.X, '-'),
    0x96 : ("IBEQ", Register.Y, '-'),
    0x97 : ("IBEQ", Register.SP, '-'),

    0xa0 : ("IBNE", Register.A, '+'),
    0xa1 : ("IBNE", Register.B, '+'),
    0xa4 : ("IBNE", Register.D, '+'),
    0xa5 : ("IBNE", Register.X, '+'),
    0xa6 : ("IBNE", Register.Y, '+'),
    0xa7 : ("IBNE", Register.SP, '+'),

    0xb0 : ("IBNE", Register.A, '-'),
    0xb1 : ("IBNE", Register.B, '-'),
    0xb4 : ("IBNE", Register.D, '-'),
    0xb5 : ("IBNE", Register.X, '-'),
    0xb6 : ("IBNE", Register.Y, '-'),
    0xb7 : ("IBNE", Register.SP, '-'),
}


##
## Transfer and Exchange Postbyte Encoding.
##
EB = {
#
# Transfers.
#
    0x00 : ("A,A"),
    0x01 : ("A,B"),
    0x02 : ("A,CCR"),
    0x03 : ("sex:A,TMP2", "SEX A,TMP2"),
    0x04 : ("sex:A,D", "SEX A,D"),
    0x05 : ("sex:A,X", "SEX A,X"),
    0x06 : ("sex:A,Y", "SEX A,Y"),
    0x07 : ("sex:A,SP", "SEX A,SP"),

    0x10 : ("B,A"),
    0x11 : ("B,B"),
    0x12 : ("B,CCR"),
    0x13 : ("sex:B,TMP2", "SEX B,TMP2"),
    0x14 : ("sex:B,D", "SEX B,D"),
    0x15 : ("sex:B,X", "SEX B,X"),
    0x16 : ("sex:B,Y", "SEX B,Y"),
    0x17 : ("sex:B,SP", "SEX B,SP"),

    0x20 : ("CCR,A"),
    0x21 : ("CCR,B"),
    0x22 : ("CCR,CCR"),
    0x23 : ("sex:CCR,TMP2", "SEX CCR,TMP2"),
    0x24 : ("sex:CCR,D", "SEX CCR,D"),
    0x25 : ("sex:CCR,X", "SEX CCR,X"),
    0x26 : ("sex:CCR,Y", "SEX CCR,Y"),
    0x27 : ("sex:CCR,SP", "SEX CCR,SP"),

    0x30 : ("TMP3,A"),
    0x31 : ("TMP3,B"),
    0x32 : ("TMP3,CCR"),
    0x33 : ("TMP3,TMP2"),
    0x34 : ("TMP3,D"),
    0x35 : ("TMP3,X"),
    0x36 : ("TMP3,Y"),
    0x37 : ("TMP3,SP"),

    0x40 : ("B,A"),
    0x41 : ("B,B"),
    0x42 : ("B,CCR"),
    0x43 : ("D,TMP2"),
    0x44 : ("D,D"),
    0x45 : ("D,X"),
    0x46 : ("D,Y"),
    0x47 : ("D,SP"),

    0x50 : ("X,A"),
    0x51 : ("X,B"),
    0x52 : ("X,CCR"),
    0x53 : ("X,TMP2"),
    0x54 : ("X,D"),
    0x55 : ("X,X"),
    0x56 : ("X,Y"),
    0x57 : ("X,SP"),

    0x60 : ("Y,A"),
    0x61 : ("Y,B"),
    0x62 : ("Y,CCR"),
    0x63 : ("Y,TMP2"),
    0x64 : ("Y,D"),
    0x65 : ("Y,X"),
    0x66 : ("Y,Y"),
    0x67 : ("Y,SP"),

    0x70 : ("SP,A"),
    0x71 : ("SP,B"),
    0x72 : ("SP,CCR"),
    0x73 : ("SP,TMP2"),
    0x74 : ("SP,D"),
    0x75 : ("SP,X"),
    0x76 : ("SP,Y"),
    0x77 : ("SP,SP"),

#
# Exchanges.
#
    0x80 : ("A,A"),
    0x81 : ("A,B"),
    0x82 : ("A,CCR"),
    0x83 : ("A,TMP2"),
    0x84 : ("A,D"),
    0x85 : ("A,X"),
    0x86 : ("A,Y"),
    0x87 : ("A,SP"),

    0x90 : ("B,A"),
    0x91 : ("B,B"),
    0x92 : ("B,CCR"),
    0x93 : ("B,TMP2"),
    0x94 : ("B,D"),
    0x95 : ("B,X"),
    0x96 : ("B,Y"),
    0x97 : ("B,SP"),

    0xa0 : ("CCR,A"),
    0xa1 : ("CCR,B"),
    0xa2 : ("CCR,CCR"),
    0xa3 : ("CCR,TMP2"),
    0xa4 : ("CCR,D"),
    0xa5 : ("CCR,X"),
    0xa6 : ("CCR,Y"),
    0xa7 : ("CCR,SP"),

    0xb0 : ("TMP3,A"),
    0xb1 : ("TMP3,B"),
    0xb2 : ("TMP3,CCR"),
    0xb3 : ("TMP3,TMP2"),
    0xb4 : ("TMP3,D"),
    0xb5 : ("TMP3,X"),
    0xb6 : ("TMP3,Y"),
    0xb7 : ("TMP3,SP"),

    0xc0 : ("B,A"),
    0xc1 : ("B,B"),
    0xc2 : ("B,CCR"),
    0xc3 : ("D,TMP2"),
    0xc4 : ("D,D"),
    0xc5 : ("D,X"),
    0xc6 : ("D,Y"),
    0xc7 : ("D,SP"),

    0xd0 : ("X,A"),
    0xd1 : ("X,B"),
    0xd2 : ("X,CCR"),
    0xd3 : ("X,TMP2"),
    0xd4 : ("X,D"),
    0xd5 : ("X,X"),
    0xd6 : ("X,Y"),
    0xd7 : ("X,SP"),

    0xe0 : ("Y,A"),
    0xe1 : ("Y,B"),
    0xe2 : ("Y,CCR"),
    0xe3 : ("Y,TMP2"),
    0xe4 : ("Y,D"),
    0xe5 : ("Y,X"),
    0xe6 : ("Y,Y"),
    0xe7 : ("Y,SP"),

    0xf0 : ("SP,A"),
    0xf1 : ("SP,B"),
    0xf2 : ("SP,CCR"),
    0xf3 : ("SP,TMP2"),
    0xf4 : ("SP,D"),
    0xf5 : ("SP,X"),
    0xf6 : ("SP,Y"),
    0xf7 : ("SP,SP"),
}


##
##  Indexed Addressing Mode Postbyte Encoding.
##
XB = {
    0x00 : ("0,X", "5b const"),
    0x01 : ("1,X", "5b const"),
    0x02 : ("2,X", "5b const"),
    0x03 : ("3,X", "5b const"),
    0x04 : ("4,X", "5b const"),
    0x05 : ("5,X", "5b const"),
    0x06 : ("6,X", "5b const"),
    0x07 : ("7,X", "5b const"),
    0x08 : ("8,X", "5b const"),
    0x09 : ("9,X", "5b const"),
    0x0a : ("10,X", "5b const"),
    0x0b : ("11,X", "5b const"),
    0x0c : ("12,X", "5b const"),
    0x0d : ("13,X", "5b const"),
    0x0e : ("14,X", "5b const"),
    0x0f : ("15,X", "5b const"),

    0x10 : ("-16,X", "5b const"),
    0x11 : ("-15,X", "5b const"),
    0x12 : ("-14,X", "5b const"),
    0x13 : ("-13,X", "5b const"),
    0x14 : ("-12,X", "5b const"),
    0x15 : ("-11,X", "5b const"),
    0x16 : ("-10,X", "5b const"),
    0x17 : ("-9,X", "5b const"),
    0x18 : ("-8,X", "5b const"),
    0x19 : ("-7,X", "5b const"),
    0x1a : ("-6,X", "5b const"),
    0x1b : ("-5,X", "5b const"),
    0x1c : ("-4,X", "5b const"),
    0x1d : ("-3,X", "5b const"),
    0x1e : ("-2,X", "5b const"),
    0x1f : ("-1,X", "5b const"),

    0x20 : ("1,+X", "pre-inc"),
    0x21 : ("2,+X", "pre-inc"),
    0x22 : ("3,+X", "pre-inc"),
    0x23 : ("4,+X", "pre-inc"),
    0x24 : ("5,+X", "pre-inc"),
    0x25 : ("6,+X", "pre-inc"),
    0x26 : ("7,+X", "pre-inc"),
    0x27 : ("8,+X", "pre-inc"),
    0x28 : ("8,-X", "pre-dec"),
    0x29 : ("7,-X", "pre-dec"),
    0x2a : ("6,-X", "pre-dec"),
    0x2b : ("5,-X", "pre-dec"),
    0x2c : ("4,-X", "pre-dec"),
    0x2d : ("3,-X", "pre-dec"),
    0x2e : ("2,-X", "pre-dec"),
    0x2f : ("1,-X", "pre-dec"),

    0x30 : ("1,X+", "post-inc"),
    0x31 : ("2,X+", "post-inc"),
    0x32 : ("3,X+", "post-inc"),
    0x33 : ("4,X+", "post-inc"),
    0x34 : ("5,X+", "post-inc"),
    0x35 : ("6,X+", "post-inc"),
    0x36 : ("7,X+", "post-inc"),
    0x37 : ("8,X+", "post-inc"),
    0x38 : ("8,X-", "post-dec"),
    0x39 : ("7,X-", "post-dec"),
    0x3a : ("6,X-", "post-dec"),
    0x3b : ("5,X-", "post-dec"),
    0x3c : ("4,X-", "post-dec"),
    0x3d : ("3,X-", "post-dec"),
    0x3e : ("2,X-", "post-dec"),
    0x3f : ("1,X-", "post-dec"),

    0x40 : ("0,Y", "5b const"),
    0x41 : ("1,Y", "5b const"),
    0x42 : ("2,Y", "5b const"),
    0x43 : ("3,Y", "5b const"),
    0x44 : ("4,Y", "5b const"),
    0x45 : ("5,Y", "5b const"),
    0x46 : ("6,Y", "5b const"),
    0x47 : ("7,Y", "5b const"),
    0x48 : ("8,Y", "5b const"),
    0x49 : ("9,Y", "5b const"),
    0x4a : ("10,Y", "5b const"),
    0x4b : ("11,Y", "5b const"),
    0x4c : ("12,Y", "5b const"),
    0x4d : ("13,Y", "5b const"),
    0x4e : ("14,Y", "5b const"),
    0x4f : ("15,Y", "5b const"),

    0x50 : ("-16,Y", "5b const"),
    0x51 : ("-15,Y", "5b const"),
    0x52 : ("-14,Y", "5b const"),
    0x53 : ("-13,Y", "5b const"),
    0x54 : ("-12,Y", "5b const"),
    0x55 : ("-11,Y", "5b const"),
    0x56 : ("-10,Y", "5b const"),
    0x57 : ("-9,Y", "5b const"),
    0x58 : ("-8,Y", "5b const"),
    0x59 : ("-7,Y", "5b const"),
    0x5a : ("-6,Y", "5b const"),
    0x5b : ("-5,Y", "5b const"),
    0x5c : ("-4,Y", "5b const"),
    0x5d : ("-3,Y", "5b const"),
    0x5e : ("-3,Y", "5b const"),
    0x5f : ("-1,Y", "5b const"),

    0x60 : ("1,+Y", "pre-inc"),
    0x61 : ("2,+Y", "pre-inc"),
    0x62 : ("3,+Y", "pre-inc"),
    0x63 : ("4,+Y", "pre-inc"),
    0x64 : ("5,+Y", "pre-inc"),
    0x65 : ("6,+Y", "pre-inc"),
    0x66 : ("7,+Y", "pre-inc"),
    0x67 : ("8,+Y", "pre-inc"),
    0x68 : ("8,-Y", "pre-dec"),
    0x69 : ("7,-Y", "pre-dec"),
    0x6a : ("6,-Y", "pre-dec"),
    0x6b : ("5,-Y", "pre-dec"),
    0x6c : ("4,-Y", "pre-dec"),
    0x6d : ("3,-Y", "pre-dec"),
    0x6e : ("2,-Y", "pre-dec"),
    0x6f : ("1,-Y", "pre-dec"),

    0x70 : ("1,Y+", "post-inc"),
    0x71 : ("2,Y+", "post-inc"),
    0x72 : ("3,Y+", "post-inc"),
    0x73 : ("4,Y+", "post-inc"),
    0x74 : ("5,Y+", "post-inc"),
    0x75 : ("6,Y+", "post-inc"),
    0x76 : ("7,Y+", "post-inc"),
    0x77 : ("8,Y+", "post-inc"),
    0x78 : ("8,Y-", "post-dec"),
    0x79 : ("7,Y-", "post-dec"),
    0x7a : ("6,Y-", "post-dec"),
    0x7b : ("5,Y-", "post-dec"),
    0x7c : ("4,Y-", "post-dec"),
    0x7d : ("3,Y-", "post-dec"),
    0x7e : ("2,Y-", "post-dec"),
    0x7f : ("1,Y-", "post-dec"),

    0x80 : ("0,SP", "5b const"),
    0x81 : ("1,SP", "5b const"),
    0x82 : ("2,SP", "5b const"),
    0x83 : ("3,SP", "5b const"),
    0x84 : ("4,SP", "5b const"),
    0x85 : ("5,SP", "5b const"),
    0x86 : ("6,SP", "5b const"),
    0x87 : ("7,SP", "5b const"),
    0x88 : ("8,SP", "5b const"),
    0x89 : ("9,SP", "5b const"),
    0x8a : ("10,SP", "5b const"),
    0x8b : ("11,SP", "5b const"),
    0x8c : ("12,SP", "5b const"),
    0x8d : ("13,SP", "5b const"),
    0x8e : ("14,SP", "5b const"),
    0x8f : ("15,SP", "5b const"),

    0x90 : ("-16,SP", "5b const"),
    0x91 : ("-15,SP", "5b const"),
    0x92 : ("-14,SP", "5b const"),
    0x93 : ("-13,SP", "5b const"),
    0x94 : ("-12,SP", "5b const"),
    0x95 : ("-11,SP", "5b const"),
    0x96 : ("-10,SP", "5b const"),
    0x97 : ("-9,SP", "5b const"),
    0x98 : ("-8,SP", "5b const"),
    0x99 : ("-7,SP", "5b const"),
    0x9a : ("-6,SP", "5b const"),
    0x9b : ("-5,SP", "5b const"),
    0x9c : ("-4,SP", "5b const"),
    0x9d : ("-3,SP", "5b const"),
    0x9e : ("-2,SP", "5b const"),
    0x9f : ("-1,SP", "5b const"),

    0xa0 : ("1,+SP", "pre-inc"),
    0xa1 : ("2,+SP", "pre-inc"),
    0xa2 : ("3,+SP", "pre-inc"),
    0xa3 : ("4,+SP", "pre-inc"),
    0xa4 : ("5,+SP", "pre-inc"),
    0xa5 : ("6,+SP", "pre-inc"),
    0xa6 : ("7,+SP", "pre-inc"),
    0xa7 : ("8,+SP", "pre-inc"),
    0xa8 : ("8,-SP", "pre-dec"),
    0xa9 : ("7,-SP", "pre-dec"),
    0xaa : ("6,-SP", "pre-dec"),
    0xab : ("5,-SP", "pre-dec"),
    0xac : ("4,-SP", "pre-dec"),
    0xad : ("3,-SP", "pre-dec"),
    0xae : ("2,-SP", "pre-dec"),
    0xaf : ("1,-SP", "pre-dec"),

    0xb0 : ("1,SP+", "post-inc"),
    0xb1 : ("2,SP+", "post-inc"),
    0xb2 : ("3,SP+", "post-inc"),
    0xb3 : ("4,SP+", "post-inc"),
    0xb4 : ("5,SP+", "post-inc"),
    0xb5 : ("6,SP+", "post-inc"),
    0xb6 : ("7,SP+", "post-inc"),
    0xb7 : ("8,SP+", "post-inc"),
    0xb8 : ("8,SP-", "post-dec"),
    0xb9 : ("7,SP-", "post-dec"),
    0xba : ("6,SP-", "post-dec"),
    0xbb : ("5,SP-", "post-dec"),
    0xbc : ("4,SP-", "post-dec"),
    0xbd : ("3,SP-", "post-dec"),
    0xbe : ("2,SP-", "post-dec"),
    0xbf : ("1,SP-", "post-dec"),

    0xc0 : ("0,PC", "5b const"),
    0xc1 : ("1,PC", "5b const"),
    0xc2 : ("2,PC", "5b const"),
    0xc3 : ("3,PC", "5b const"),
    0xc4 : ("4,PC", "5b const"),
    0xc5 : ("5,PC", "5b const"),
    0xc6 : ("6,PC", "5b const"),
    0xc7 : ("7,PC", "5b const"),
    0xc8 : ("8,PC", "5b const"),
    0xc9 : ("9,PC", "5b const"),
    0xca : ("10,PC", "5b const"),
    0xcb : ("11,PC", "5b const"),
    0xcc : ("12,PC", "5b const"),
    0xcd : ("13,PC", "5b const"),
    0xce : ("14,PC", "5b const"),
    0xcf : ("15,PC", "5b const"),

    0xd0 : ("-16,PC", "5b const"),
    0xd1 : ("-15,PC", "5b const"),
    0xd2 : ("-14,PC", "5b const"),
    0xd3 : ("-13,PC", "5b const"),
    0xd4 : ("-12,PC", "5b const"),
    0xd5 : ("-11,PC", "5b const"),
    0xd6 : ("-10,PC", "5b const"),
    0xd7 : ("-9,PC", "5b const"),
    0xd8 : ("-8,PC", "5b const"),
    0xd9 : ("-7,PC", "5b const"),
    0xda : ("-6,PC", "5b const"),
    0xdb : ("-5,PC", "5b const"),
    0xdc : ("-4,PC", "5b const"),
    0xdd : ("-3,PC", "5b const"),
    0xde : ("-2,PC", "5b const"),
    0xdf : ("-1,PC", "5b const"),

    0xe0 : ("%s,X", "9b const"),
    0xe1 : ("-%s,X", "9b const"),
    0xe2 : ("%s,X", "16b const"),
    0xe3 : ("[%s,X]", "16b indr"),
    0xe4 : ("A,X", "A offset"),
    0xe5 : ("B,X", "B offset"),
    0xe6 : ("D,X", "D offset"),
    0xe7 : ("[D,X]", "D indr"),
    0xe8 : ("%s,Y", "9b const"),
    0xe9 : ("-%s,Y", "9b const"),
    0xea : ("%s,Y", "16b const"),
    0xeb : ("[%s,Y]", "16b indr"),
    0xec : ("A,Y", "A offset"),
    0xed : ("B,Y", "B offset"),
    0xee : ("D,Y", "D offset"),
    0xef : ("[D,Y]", "D indr"),

    0xf0 : ("%s,SP", "9b const"),
    0xf1 : ("-%s,SP", "9b const"),
    0xf2 : ("%s,SP", "16b const"),
    0xf3 : ("[%s,SP]", "16b indr"),
    0xf4 : ("A,SP", "A offset"),
    0xf5 : ("B,SP", "B offset"),
    0xf6 : ("D,SP", "D offset"),
    0xf7 : ("[D,SP]", "D indr"),
    0xf8 : ("%s,PC", "9b const"),
    0xf9 : ("-%s,PC", "9b const"),
    0xfa : ("%s,PC", "16 const"),   # check: 16b const???
    0xfb : ("[%s,PC]", "16b indr"),
    0xfc : ("A,PC", "A offset"),
    0xfd : ("B,PC", "B offset"),
    0xfe : ("D,PC", "D offset"),
    0xff : ("[D,PC]", "D indr"),
}

# AdressingMode
IH      = 0
RL      = 1
ID      = 2
EX      = 3
IM      = 4
DI      = 5
SPECIAL = 6

opcodeMapPage1 ={
    0x00 : ("BGND", 5, IH, 1),
    0x01 : ("MEM", 5, IH, 1),
    0x02 : ("INY", 1, IH, 1),
    0x03 : ("DEY", 1, IH, 1),
    0x04 : ("*loop*", 3, RL, 3),
    0x05 : ("JMP", '3-6', ID, '2-4'),
    0x06 : ("JMP", 3, EX, 3),
    0x07 : ("BSR", 4, RL, 2),
    0x08 : ("INX", 1, IH, 1),
    0x09 : ("DEX", 1, IH, 1),
    0x0a : ("RTC", 6, IH, 1),
    0x0b : ("RTI", 8, IH, 1),
    0x0c : ("BSET", '4-6', ID, '3-5'),
    0x0d : ("BCLR", '4-6', ID, '3-5'),
    0x0e : ("BRSET", '4-8', ID, '4-6'),
    0x0f : ("BRCLR", '4-8', ID, '4-6'),

    0x10 : ("ANDCC", 1, IM, 2),
    0x11 : ("EDIV", 11, IH, 1),
    0x12 : ("MUL", 3, IH, 1),
    0x13 : ("EMUL", 3, IH, 1),
    0x14 : ("ORCC", 1, IM, 2),
    0x15 : ("JSR", '4-7', ID, '2-4'),
    0x16 : ("JSR", 4, EX, 3),
    0x17 : ("JSR", 4, DI, 2),
    0x18 : ("*page-2*", None, None, None),
    0x19 : ("LEAY", 2, ID, '2-4'),
    0x1a : ("LEAX", 2, ID, '2-4'),
    0x1b : ("LEAS", 2, ID, '2-4'),
    0x1c : ("BSET", 4, EX, 4),
    0x1d : ("BCLR", 4, EX, 4),
    0x1e : ("BRSET", 5, EX, 5),
    0x1f : ("BRCLR", 5, EX, 5),

    0x20 : ("BRA", 3, RL, 2),
    0x21 : ("BRN", 1, RL, 2),
    0x22 : ("BHI", '3/1', RL, 2),
    0x23 : ("BLS", '3/1', RL, 2),
    0x24 : ("BCC", '3/1', RL, 2),
    0x25 : ("BCS", '3/1', RL, 2),
    0x26 : ("BNE", '3/1', RL, 2),
    0x27 : ("BEQ", '3/1', RL, 2),
    0x28 : ("BVC", '3/1', RL, 2),
    0x29 : ("BVS", '3/1', RL, 2),
    0x2a : ("BPL", '3/1', RL, 2),
    0x2b : ("BMI", '3/1', RL, 2),
    0x2c : ("BGE", '3/1', RL, 2),
    0x2d : ("BLT", '3/1', RL, 2),
    0x2e : ("BGT", '3/1', RL, 2),
    0x2f : ("BLE", '3/1', RL, 2),

    0x30 : ("PULX", 3, IH, 1),
    0x31 : ("PULY", 3, IH, 1),
    0x32 : ("PULA", 3, IH, 1),
    0x33 : ("PULB", 3, IH, 1),
    0x34 : ("PSHX", 2, IH, 1),
    0x35 : ("PSHY", 2, IH, 1),
    0x36 : ("PSHA", 2, IH, 1),
    0x37 : ("PSHB", 2, IH, 1),
    0x38 : ("PULC", 3, IH, 1),
    0x39 : ("PSHC", 2, IH, 1),
    0x3a : ("PULD", 3, IH, 1),
    0x3b : ("PSHD", 2, IH, 1),
    0x3c : ("WAV (continued)", '*+9', SPECIAL, 1),  # ist continued richtig???
    0x3d : ("RTS", 5, IH, 1),
    0x3e : ("WAI", 8, IH, 1),
    0x3f : ("SWI", 9, IH, 1),

    0x40 : ("NEGA", 1, IH, 1),
    0x41 : ("COMA", 1, IH, 1),
    0x42 : ("INCA", 1, IH, 1),
    0x43 : ("DECA", 1, IH, 1),
    0x44 : ("LSRA", 1, IH, 1),
    0x45 : ("ROLA", 1, IH, 1),
    0x46 : ("RORA", 1, IH, 1),
    0x47 : ("ASRA", 1, IH, 1),
    0x48 : ("ASLA", 1, IH, 1),
    0x49 : ("LSRD", 1, IH, 1),
    0x4a : ("CALL", 8, EX, 4),
    0x4b : ("CALL", '8-10', ID, '2-5'),
    0x4c : ("BSET", 4, DI, 3),
    0x4d : ("BCLR", 4, DI, 3),
    0x4e : ("BRSET", 4, DI, 4),
    0x4f : ("BRCLR", 4, DI, 4),

    0x50 : ("NEGB", 1, IH, 1),
    0x51 : ("COMB", 1, IH, 1),
    0x52 : ("INCB", 1, IH, 1),
    0x53 : ("DECB", 1, IH, 1),
    0x54 : ("LSRB", 1, IH, 1),
    0x55 : ("ROLB", 1, IH, 1),
    0x56 : ("RORB", 1, IH, 1),
    0x57 : ("ASRB", 1, IH, 1),
    0x58 : ("ASLB", 1, IH, 1),
    0x59 : ("ASLD", 1, IH, 1),
    0x5a : ("STAA", 2, DI, 2),
    0x5b : ("STAB", 2, DI, 2),
    0x5c : ("STD", 2, DI, 2),
    0x5d : ("STY", 2, DI, 2),
    0x5e : ("STX", 2, DI, 2),
    0x5f : ("STS", 2, DI, 2),

    0x60 : ("NEG", '3-6', ID, '2-4'),
    0x61 : ("COM", '3-6', ID, '2-4'),
    0x62 : ("INC", '3-6', ID, '2-4'),
    0x63 : ("DEC", '3-6', ID, '2-4'),
    0x64 : ("LSR", '3-6', ID, '2-4'),
    0x65 : ("ROL", '3-6', ID, '2-4'),
    0x66 : ("ROR", '3-6', ID, '2-4'),
    0x67 : ("ASR", '3-6', ID, '2-4'),
    0x68 : ("ASL", '3-6', ID, '2-4'),
    0x69 : ("CLR", '2-5', ID, '2-4'),
    0x6a : ("STAA", '2-5', ID, '2-4'),
    0x6b : ("STAB", '2-5', ID, '2-4'),
    0x6c : ("STD", '2-5', ID, '2-4'),
    0x6d : ("STY", '2-5', ID, '2-4'),
    0x6e : ("STX", '2-5', ID, '2-4'),
    0x6f : ("STS", '2-5', ID, '2-4'),

    0x70 : ("NEG", 4, EX, 3),
    0x71 : ("COM", 4, EX, 3),
    0x72 : ("INC", 4, EX, 3),
    0x73 : ("DEC", 4, EX, 3),
    0x74 : ("LSR", 4, EX, 3),
    0x75 : ("ROL", 4, EX, 3),
    0x76 : ("ROR", 4, EX, 3),
    0x77 : ("ASR", 4, EX, 3),
    0x78 : ("ASL", 4, EX, 3),
    0x79 : ("CLR", 3, EX, 3),
    0x7a : ("STAA", 3, EX, 3),
    0x7b : ("STAB", 3, EX, 3),
    0x7c : ("STD", 3, EX, 3),
    0x7d : ("STY", 3, EX, 3),
    0x7e : ("STX", 3, EX, 3),
    0x7f : ("STS", 3, EX, 3),

    0x80 : ("SUBA", 1, IM, 2),
    0x81 : ("CMPA", 1, IM, 2),
    0x82 : ("SBCA", 1, IM, 2),
    0x83 : ("SUBD", 1, IM, 3),
    0x84 : ("ANDA", 1, IM, 2),
    0x85 : ("BITA", 1, IM, 2),
    0x86 : ("LDAA", 1, IM, 2),
    0x87 : ("CLRA", 1, IH, 1),
    0x88 : ("EORA", 1, IM, 2),
    0x89 : ("ADCA", 1, IM, 2),
    0x8a : ("ORAA", 1, IM, 2),
    0x8b : ("ADDA", 1, IM, 2),
    0x8c : ("CPD", 2, IM, 3),
    0x8d : ("CPY", 2, IM, 3),
    0x8e : ("CPX", 2, IM, 3),
    0x8f : ("CPS", 2, IM, 3),

    0x90 : ("SUBA", 3, DI, 2),
    0x91 : ("CMPA", 3, DI, 2),
    0x92 : ("SBCA", 3, DI, 2),
    0x93 : ("SUBD", 3, DI, 2),
    0x94 : ("ANDA", 3, DI, 2),
    0x95 : ("BITA", 3, DI, 2),
    0x96 : ("LDAA", 3, DI, 2),
    0x97 : ("TSTA", 1, IH, 1),
    0x98 : ("EORA", 3, DI, 2),
    0x99 : ("ADCA", 3, DI, 2),
    0x9a : ("ORAA", 3, DI, 2),
    0x9b : ("ADDA", 3, DI, 2),
    0x9c : ("CPD", 3, DI, 2),
    0x9d : ("CPY", 3, DI, 2),
    0x9e : ("CPX", 3, DI, 2),
    0x9f : ("CPS", 3, DI, 2),

    0xa0 : ("SUBA", '3-6', ID , '2-4'),
    0xa1 : ("CMPA", '3-6', ID , '2-4'),
    0xa2 : ("SBCA", '3-6', ID , '2-4'),
    0xa3 : ("SUBD", '3-6', ID , '2-4'),
    0xa4 : ("ANDA", '3-6', ID , '2-4'),
    0xa5 : ("BITA", '3-6', ID , '2-4'),
    0xa6 : ("LDAA", '3-6', ID , '2-4'),
    0xa7 : ("Nmnemonic", 1, IH, 1),
    0xa8 : ("EORA", '3-6', ID , '2-4'),
    0xa9 : ("ADCA", '3-6', ID , '2-4'),
    0xaa : ("ORAA", '3-6', ID , '2-4'),
    0xab : ("ADDA", '3-6', ID , '2-4'),
    0xac : ("CPD", '3-6', ID , '2-4'),
    0xad : ("CPY", '3-6', ID , '2-4'),
    0xae : ("CPX", '3-6', ID , '2-4'),
    0xaf : ("CPS", '3-6', ID , '2-4'),

    0xb0 : ("SUBA", 3, EX, 3),
    0xb1 : ("CMPA", 3, EX, 3),
    0xb2 : ("SBCA", 3, EX, 3),
    0xb3 : ("SUBD", 3, EX, 3),
    0xb4 : ("ANDA", 3, EX, 3),
    0xb5 : ("BITA", 3, EX, 3),
    0xb6 : ("LDAA", 3, EX, 3),
    0xb7 : ("*tfr/exg*", 1, IH, 2),
    0xb8 : ("EORA", 3, EX, 3),
    0xb9 : ("ADCA", 3, EX, 3),
    0xba : ("ORAA", 3, EX, 3),
    0xbb : ("ADDA", 3, EX, 3),
    0xbc : ("CPD", 3, EX, 3),
    0xbd : ("CPY", 3, EX, 3),
    0xbe : ("CPX", 3, EX, 3),
    0xbf : ("CPS", 3, EX, 3),

    0xc0 : ("SUBB", 1, IM, 2),
    0xc1 : ("CMPB", 1, IM, 2),
    0xc2 : ("SBCB", 1, IM, 2),
    0xc3 : ("ADDD", 2, IM, 3),
    0xc4 : ("ANDB", 1, IM, 2),
    0xc5 : ("BITB", 1, IM, 2),
    0xc6 : ("LDAB", 1, IM, 2),
    0xc7 : ("CLRB", 1, IH, 1),
    0xc8 : ("EORB", 1, IM, 2),
    0xc9 : ("ADCB", 1, IM, 2),
    0xca : ("ORAB", 1, IM, 2),
    0xcb : ("ADDB", 1, IM, 2),
    0xcc : ("LDD", 2, IM, 3),
    0xcd : ("LDY", 2, IM, 3),
    0xce : ("LDX", 2, IM, 3),
    0xcf : ("LDS", 2, IM, 3),

    0xd0 : ("SUBB", 3, DI, 2),
    0xd1 : ("CMPB", 3, DI, 2),
    0xd2 : ("SBCB", 3, DI, 2),
    0xd3 : ("ADDD", 3, DI, 2),
    0xd4 : ("ANDB", 3, DI, 2),
    0xd5 : ("BITB", 3, DI, 2),
    0xd6 : ("LDAB", 3, DI, 2),
    0xd7 : ("TSTB", 1, IH, 1),
    0xd8 : ("EORB", 3, DI, 2),
    0xd9 : ("ADCB", 3, DI, 2),
    0xda : ("ORAB", 3, DI, 2),
    0xdb : ("ADDB", 3, DI, 2),
    0xdc : ("LDD", 3, DI, 2),
    0xdd : ("LDY", 3, DI, 2),
    0xde : ("LDX", 3, DI, 2),
    0xdf : ("LDS", 3, DI, 2),

    0xe0 : ("SUBB", '3-6', ID, '2-4'),
    0xe1 : ("CMPB", '3-6', ID, '2-4'),
    0xe2 : ("SBCB", '3-6', ID, '2-4'),
    0xe3 : ("ADDD", '3-6', ID, '2-4'),
    0xe4 : ("ANDB", '3-6', ID, '2-4'),
    0xe5 : ("BITB", '3-6', ID, '2-4'),
    0xe6 : ("LDAB", '3-6', ID, '2-4'),
    0xe7 : ("TST", '3-6', ID, '2-4'),
    0xe8 : ("EORB", '3-6', ID, '2-4'),
    0xe9 : ("ADCB", '3-6', ID, '2-4'),
    0xea : ("ORAB", '3-6', ID, '2-4'),
    0xeb : ("ADDB", '3-6', ID, '2-4'),
    0xec : ("LDD", '3-6', ID, '2-4'),
    0xed : ("LDY", '3-6', ID, '2-4'),
    0xee : ("LDX", '3-6', ID, '2-4'),
    0xef : ("LDS", '3-6', ID, '2-4'),

    0xf0 : ("SUBB", 3, EX, 3),
    0xf1 : ("CMPB", 3, EX, 3),
    0xf2 : ("SBCB", 3, EX, 3),
    0xf3 : ("ADDD", 3, EX, 3),
    0xf4 : ("ANDB", 3, EX, 3),
    0xf5 : ("BITB", 3, EX, 3),
    0xf6 : ("LDAB", 3, EX, 3),
    0xf7 : ("TST", 3, EX, 3),
    0xf8 : ("EORB", 3, EX, 3),
    0xf9 : ("ADCB", 3, EX, 3),
    0xfa : ("ORAB", 3, EX, 3),
    0xfb : ("ADDB", 3, EX, 3),
    0xfc : ("LDD", 3, EX, 3),
    0xfd : ("LDY", 3, EX, 3),
    0xfe : ("LDX", 3, EX, 3),
    0xff : ("LDS", 3, EX, 3),
}


TFR_EXG = 0xb7
PAGE_TWO = 0x18
LOOP = 0x04

opcodeMapPage2 ={
    0x00 : ("MOVW", 4, 'im-id', 5),
    0x01 : ("MOVW", 5, 'ex-id', 5),
    0x02 : ("MOVW", 5, 'id-id', 4),
    0x03 : ("MOVW", 5, 'im-ex', 6),
    0x04 : ("MOVW", 6, 'ex-ex', 6),
    0x05 : ("MOVW", 5, 'id-ex', 5),
    0x06 : ("ABA", 2, IH, 2),
    0x07 : ("DAA", 3, IH, 2),
    0x08 : ("MOVB", 4, 'im-id', 4),
    0x09 : ("MOVB", 5, 'ex-id', 5),
    0x0a : ("MOVB", 5, 'id-id', 4),
    0x0b : ("MOVB", 4, 'im-ex', 5),
    0x0c : ("MOVB", 6, 'ex-ex', 6),
    0x0d : ("MOVB", 5, 'id-ex', 5),
    0x0e : ("TAB", 2, IH, 2),
    0x0f : ("TBA", 2, IH,2 ),

    0x10 : ("IDIV", 12, IH, 2),
    0x11 : ("FDIV", 12, IH, 2),
    0x12 : ("EMACS", 13, SPECIAL, 4),
    0x13 : ("EMULS", 3, IH, 2),
    0x14 : ("EDIVS", 12, IH, 2),
    0x15 : ("IDIVS", 12, IH, 2),
    0x16 : ("SBA", 2, IH, 2),
    0x17 : ("CBA", 2, IH, 2),
    0x18 : ("MAXA", '4-7', ID, '3-5'),
    0x19 : ("MINA", '4-7', ID, '3-5'),
    0x1a : ("EMAXD", '4-7', ID, '3-5'),
    0x1b : ("EMIND", '4-7', ID, '3-5'),
    0x1c : ("MAXM", '4-7', ID, '3-5'),
    0x1d : ("MINM", '4-7', ID, '3-5'),
    0x1e : ("EMAXM", '4-7', ID, '3-5'),
    0x1f : ("EMINM", '4-7', ID, '3-5'),

    0x20 : ("LBRA", 4, RL, 4),
    0x21 : ("LBRN", 3, RL, 4),
    0x22 : ("LBHI", '4/3', RL, 4),
    0x23 : ("LBLS", '4/3', RL, 4),
    0x24 : ("LBCC", '4/3', RL, 4),
    0x25 : ("LBCS", '4/3', RL, 4),
    0x26 : ("LBNE", '4/3', RL, 4),
    0x27 : ("LBEQ", '4/3', RL, 4),
    0x28 : ("LBVC", '4/3', RL, 4),
    0x29 : ("LBVS", '4/3', RL, 4),
    0x2a : ("LBPL", '4/3', RL, 4),
    0x2b : ("LBMI", '4/3', RL, 4),
    0x2c : ("LBGE", '4/3', RL, 4),
    0x2d : ("LBLT", '4/3', RL, 4),
    0x2e : ("LBGT", '4/3', RL, 4),
    0x2f : ("LBLE", '4/3', RL, 4),

    0x30 : ("TRAP", 10, IH, 2),
    0x31 : ("TRAP", 10, IH, 2),
    0x32 : ("TRAP", 10, IH, 2),
    0x33 : ("TRAP", 10, IH, 2),
    0x34 : ("TRAP", 10, IH, 2),
    0x35 : ("TRAP", 10, IH, 2),
    0x36 : ("TRAP", 10, IH, 2),
    0x37 : ("TRAP", 10, IH, 2),
    0x38 : ("TRAP", 10, IH, 2),
    0x39 : ("TRAP", 10, IH, 2),
    0x3a : ("REV", "*3n", SPECIAL, 2),
    0x3b : ("REVW", "*3n", SPECIAL, 2),
    0x3c : ("WAV", "*8B", SPECIAL, 2),
    0x3d : ("TBL", 8, ID, 3),
    0x3e : ("STOP", "*9+5", IH, 2),
    0x3f : ("ETBL", 10, ID, 3),

    0x40 : ("TRAP", 10, IH, 2),
    0x41 : ("TRAP", 10, IH, 2),
    0x42 : ("TRAP", 10, IH, 2),
    0x43 : ("TRAP", 10, IH, 2),
    0x44 : ("TRAP", 10, IH, 2),
    0x45 : ("TRAP", 10, IH, 2),
    0x46 : ("TRAP", 10, IH, 2),
    0x47 : ("TRAP", 10, IH, 2),
    0x48 : ("TRAP", 10, IH, 2),
    0x49 : ("TRAP", 10, IH, 2),
    0x4a : ("TRAP", 10, IH, 2),
    0x4b : ("TRAP", 10, IH, 2),
    0x4c : ("TRAP", 10, IH, 2),
    0x4d : ("TRAP", 10, IH, 2),
    0x4e : ("TRAP", 10, IH, 2),
    0x4f : ("TRAP", 10, IH, 2),

    0x50 : ("TRAP", 10, IH, 2),
    0x51 : ("TRAP", 10, IH, 2),
    0x52 : ("TRAP", 10, IH, 2),
    0x53 : ("TRAP", 10, IH, 2),
    0x54 : ("TRAP", 10, IH, 2),
    0x55 : ("TRAP", 10, IH, 2),
    0x56 : ("TRAP", 10, IH, 2),
    0x57 : ("TRAP", 10, IH, 2),
    0x58 : ("TRAP", 10, IH, 2),
    0x59 : ("TRAP", 10, IH, 2),
    0x5a : ("TRAP", 10, IH, 2),
    0x5b : ("TRAP", 10, IH, 2),
    0x5c : ("TRAP", 10, IH, 2),
    0x5d : ("TRAP", 10, IH, 2),
    0x5e : ("TRAP", 10, IH, 2),
    0x5f : ("TRAP", 10, IH, 2),

    0x60 : ("TRAP", 10, IH, 2),
    0x61 : ("TRAP", 10, IH, 2),
    0x62 : ("TRAP", 10, IH, 2),
    0x63 : ("TRAP", 10, IH, 2),
    0x64 : ("TRAP", 10, IH, 2),
    0x65 : ("TRAP", 10, IH, 2),
    0x66 : ("TRAP", 10, IH, 2),
    0x67 : ("TRAP", 10, IH, 2),
    0x68 : ("TRAP", 10, IH, 2),
    0x69 : ("TRAP", 10, IH, 2),
    0x6a : ("TRAP", 10, IH, 2),
    0x6b : ("TRAP", 10, IH, 2),
    0x6c : ("TRAP", 10, IH, 2),
    0x6d : ("TRAP", 10, IH, 2),
    0x6e : ("TRAP", 10, IH, 2),
    0x6f : ("TRAP", 10, IH, 2),

    0x70 : ("TRAP", 10, IH, 2),
    0x71 : ("TRAP", 10, IH, 2),
    0x72 : ("TRAP", 10, IH, 2),
    0x73 : ("TRAP", 10, IH, 2),
    0x74 : ("TRAP", 10, IH, 2),
    0x75 : ("TRAP", 10, IH, 2),
    0x76 : ("TRAP", 10, IH, 2),
    0x77 : ("TRAP", 10, IH, 2),
    0x78 : ("TRAP", 10, IH, 2),
    0x79 : ("TRAP", 10, IH, 2),
    0x7a : ("TRAP", 10, IH, 2),
    0x7b : ("TRAP", 10, IH, 2),
    0x7c : ("TRAP", 10, IH, 2),
    0x7d : ("TRAP", 10, IH, 2),
    0x7e : ("TRAP", 10, IH, 2),
    0x7f : ("TRAP", 10, IH, 2),

    0x80 : ("TRAP", 10, IH, 2),
    0x81 : ("TRAP", 10, IH, 2),
    0x82 : ("TRAP", 10, IH, 2),
    0x83 : ("TRAP", 10, IH, 2),
    0x84 : ("TRAP", 10, IH, 2),
    0x85 : ("TRAP", 10, IH, 2),
    0x86 : ("TRAP", 10, IH, 2),
    0x87 : ("TRAP", 10, IH, 2),
    0x88 : ("TRAP", 10, IH, 2),
    0x89 : ("TRAP", 10, IH, 2),
    0x8a : ("TRAP", 10, IH, 2),
    0x8b : ("TRAP", 10, IH, 2),
    0x8c : ("TRAP", 10, IH, 2),
    0x8d : ("TRAP", 10, IH, 2),
    0x8e : ("TRAP", 10, IH, 2),
    0x8f : ("TRAP", 10, IH, 2),

    0x90 : ("TRAP", 10, IH, 2),
    0x91 : ("TRAP", 10, IH, 2),
    0x92 : ("TRAP", 10, IH, 2),
    0x93 : ("TRAP", 10, IH, 2),
    0x94 : ("TRAP", 10, IH, 2),
    0x95 : ("TRAP", 10, IH, 2),
    0x96 : ("TRAP", 10, IH, 2),
    0x97 : ("TRAP", 10, IH, 2),
    0x98 : ("TRAP", 10, IH, 2),
    0x99 : ("TRAP", 10, IH, 2),
    0x9a : ("TRAP", 10, IH, 2),
    0x9b : ("TRAP", 10, IH, 2),
    0x9c : ("TRAP", 10, IH, 2),
    0x9d : ("TRAP", 10, IH, 2),
    0x9e : ("TRAP", 10, IH, 2),
    0x9f : ("TRAP", 10, IH, 2),

    0xa0 : ("TRAP", 10, IH, 2),
    0xa1 : ("TRAP", 10, IH, 2),
    0xa2 : ("TRAP", 10, IH, 2),
    0xa3 : ("TRAP", 10, IH, 2),
    0xa4 : ("TRAP", 10, IH, 2),
    0xa5 : ("TRAP", 10, IH, 2),
    0xa6 : ("TRAP", 10, IH, 2),
    0xa7 : ("TRAP", 10, IH, 2),
    0xa8 : ("TRAP", 10, IH, 2),
    0xa9 : ("TRAP", 10, IH, 2),
    0xaa : ("TRAP", 10, IH, 2),
    0xab : ("TRAP", 10, IH, 2),
    0xac : ("TRAP", 10, IH, 2),
    0xad : ("TRAP", 10, IH, 2),
    0xae : ("TRAP", 10, IH, 2),
    0xaf : ("TRAP", 10, IH, 2),

    0xb0 : ("TRAP", 10, IH, 2),
    0xb1 : ("TRAP", 10, IH, 2),
    0xb2 : ("TRAP", 10, IH, 2),
    0xb3 : ("TRAP", 10, IH, 2),
    0xb4 : ("TRAP", 10, IH, 2),
    0xb5 : ("TRAP", 10, IH, 2),
    0xb6 : ("TRAP", 10, IH, 2),
    0xb7 : ("TRAP", 10, IH, 2),
    0xb8 : ("TRAP", 10, IH, 2),
    0xb9 : ("TRAP", 10, IH, 2),
    0xba : ("TRAP", 10, IH, 2),
    0xbb : ("TRAP", 10, IH, 2),
    0xbc : ("TRAP", 10, IH, 2),
    0xbd : ("TRAP", 10, IH, 2),
    0xbe : ("TRAP", 10, IH, 2),
    0xbf : ("TRAP", 10, IH, 2),

    0xc0 : ("TRAP", 10, IH, 2),
    0xc1 : ("TRAP", 10, IH, 2),
    0xc2 : ("TRAP", 10, IH, 2),
    0xc3 : ("TRAP", 10, IH, 2),
    0xc4 : ("TRAP", 10, IH, 2),
    0xc5 : ("TRAP", 10, IH, 2),
    0xc6 : ("TRAP", 10, IH, 2),
    0xc7 : ("TRAP", 10, IH, 2),
    0xc8 : ("TRAP", 10, IH, 2),
    0xc9 : ("TRAP", 10, IH, 2),
    0xca : ("TRAP", 10, IH, 2),
    0xcb : ("TRAP", 10, IH, 2),
    0xcc : ("TRAP", 10, IH, 2),
    0xcd : ("TRAP", 10, IH, 2),
    0xce : ("TRAP", 10, IH, 2),
    0xcf : ("TRAP", 10, IH, 2),

    0xd0 : ("TRAP", 10, IH, 2),
    0xd1 : ("TRAP", 10, IH, 2),
    0xd2 : ("TRAP", 10, IH, 2),
    0xd3 : ("TRAP", 10, IH, 2),
    0xd4 : ("TRAP", 10, IH, 2),
    0xd5 : ("TRAP", 10, IH, 2),
    0xd6 : ("TRAP", 10, IH, 2),
    0xd7 : ("TRAP", 10, IH, 2),
    0xd8 : ("TRAP", 10, IH, 2),
    0xd9 : ("TRAP", 10, IH, 2),
    0xda : ("TRAP", 10, IH, 2),
    0xdb : ("TRAP", 10, IH, 2),
    0xdc : ("TRAP", 10, IH, 2),
    0xdd : ("TRAP", 10, IH, 2),
    0xde : ("TRAP", 10, IH, 2),
    0xdf : ("TRAP", 10, IH, 2),

    0xe0 : ("TRAP", 10, IH, 2),
    0xe1 : ("TRAP", 10, IH, 2),
    0xe2 : ("TRAP", 10, IH, 2),
    0xe3 : ("TRAP", 10, IH, 2),
    0xe4 : ("TRAP", 10, IH, 2),
    0xe5 : ("TRAP", 10, IH, 2),
    0xe6 : ("TRAP", 10, IH, 2),
    0xe7 : ("TRAP", 10, IH, 2),
    0xe8 : ("TRAP", 10, IH, 2),
    0xe9 : ("TRAP", 10, IH, 2),
    0xea : ("TRAP", 10, IH, 2),
    0xeb : ("TRAP", 10, IH, 2),
    0xec : ("TRAP", 10, IH, 2),
    0xed : ("TRAP", 10, IH, 2),
    0xee : ("TRAP", 10, IH, 2),
    0xef : ("TRAP", 10, IH, 2),

    0xf0 : ("TRAP", 10, IH, 2),
    0xf1 : ("TRAP", 10, IH, 2),
    0xf2 : ("TRAP", 10, IH, 2),
    0xf3 : ("TRAP", 10, IH, 2),
    0xf4 : ("TRAP", 10, IH, 2),
    0xf5 : ("TRAP", 10, IH, 2),
    0xf6 : ("TRAP", 10, IH, 2),
    0xf7 : ("TRAP", 10, IH, 2),
    0xf8 : ("TRAP", 10, IH, 2),
    0xf9 : ("TRAP", 10, IH, 2),
    0xfa : ("TRAP", 10, IH, 2),
    0xfb : ("TRAP", 10, IH, 2),
    0xfc : ("TRAP", 10, IH, 2),
    0xfd : ("TRAP", 10, IH, 2),
    0xfe : ("TRAP", 10, IH, 2),
    0xff : ("TRAP", 10, IH, 2),
}


class AlignmentError(Exception): pass

##
##  Page-Size-Option: [8, 16, 32, 64, 128, 256, 512, 1024]
##
class CachedMemory(object):
    def __init__(self, readFunc, pagesize = 64):
        self.pagesize = pagesize
        self.readFunc = readFunc
        self.flushCache()

    def getByte(self, address):
        page,offset = self.getPageAddress(address)
        if page not in self.cache:
            data = self.readFunc(page, self.pagesize)
            self.cache[page] = data
            #print map(hex,data)
        return self.cache[page][offset]

    def getWord(self, address):
        if (address & 0x0001) == 0x0001:
            raise AlignmentError, "Address must be word aligned."
        page, offset = self.getPageAddress(address)
        if page not in self.cache:
            # todo: Log (DEBUG)!!!
            data = self.readFunc(page, self.pagesize)
            self.cache[page] = data
        pageData = self.cache[page]
        return ((pageData[offset]) << 8) | (pageData[offset + 1])

    def getPageAddress(self, address):
        return address & ~(self.pagesize - 1), address % self.pagesize

    def readPage(self, address):
        page = self.getPageAddress(address)
        print hex(address),hex(page)

    def flushCache(self):
        '''
        Option:
            if you don't trust the integrety of your Flash/EEPROM
            or
            if you are using self-modifying code.
        '''
        self.cache = {}

    def flushPage(self, address):
        page = self.getPageAddress(address)
        if self.cache.has_key(page):
            self.cache.pop(address)


tfrOrExg = lambda postbyte: postbyte>=0x80 and 'EXG' or 'TFR'
isBitFunction = lambda fn: fn in ('BSET', 'BCLR')
isBitBranchFunction = lambda fn: fn in ('BRSET', 'BRCLR')


# 0x4320 20 -- LBRA	0x4342 eigentlich 43B1!?
# 0x570D 63 -- DEC	7,PC    must be: 0x570D 63C7 DEC     5716,PCR

def disasm(addr, data):
    pc = addr
    op = data.getByte(pc)
    mnemonic, cycles, mode, size = opcodeMapPage1.get(op, None)
    print "0x%04X %02x -- '%s'" % (pc, data.getByte(pc), mnemonic)
    operand = ''
    xb = None
    lb = None
    while True:
        pc += size
        pc &= 0xffff
        op = data.getByte(pc)
        operand = ''
        mnemonic, cycles, mode, size = opcodeMapPage1.get(op, None)

        if pc == 0x570D:
            pass

        if op == PAGE_TWO:
            op = data.getByte(pc + 1)
            mnemonic, cycles, mode, size = opcodeMapPage2.get(op, None)
        elif op == TFR_EXG:
            op = data.getByte(pc + 1)
            eb = EB[op]
            mnemonic, operand = tfrOrExg(op), eb

        if mode == IH:
            pass
        elif mode == IM:
            if size == 2:
                operand = '#$%02X' % data.getByte(pc + 1)
            elif size == 3:
                operand = '#$%04X' % ((data.getByte(pc + 1) << 8) | data.getByte(pc + 2),)
            else:
                raise NotImplementedError
        elif mode == ID:
            op2 = data.getByte(pc + 1)
            xb = XB[op2]
            operand = xb[0]
            if xb[1] == '5b const':
                if isBitFunction(mnemonic):
                    size = 3
                    mm = data.getByte(pc + 2)
                    operand +=  " #$%02X" % mm
                elif isBitBranchFunction(mnemonic):
                    size = 4
                else:
                    size = 2
            elif xb[1] == '9b const':
                if isBitFunction(mnemonic):
                    pass
                elif isBitBranchFunction(mnemonic):
                    pass
                const = data.getByte(pc + 2)
                if (op2 & 0x01) == 0x01:
                    const = (~const & 0xff) + 1
                size = 3
                operand = operand % ("$%02X" % const)
            elif xb[1] == '16b const':
                const = ((data.getByte(pc + 2) << 8) | data.getByte(pc + 3))
                operand = operand % ("$%04X" % const)
                size = 4
            elif xb[1] == '16b indr':
                const = ((data.getByte(pc + 2) << 8) | data.getByte(pc + 3))
                operand = operand % ("$%04X" % const)
                size = 4
            elif xb[1] == 'A offset':
                #operand +=  " #$%02X" % data.getByte(pc+2)
                size = 2
                pass    # ???
            elif xb[1] == 'D offset':
                size = 2
            elif xb[1] == 'D indr':
                size = 2    # data.getByte(pc+2)
            elif xb[1] == 'B offset':
                operand +=  " #$%02X" % data.getByte(pc+2)
                size = 3
            elif xb[1] == 'pre-inc':
                size = 2
            elif xb[1] == 'pre-dec':
                size = 2
            elif xb[1] == 'post-inc':
                size = 2
            elif xb[1] == 'post-dec':
                size = 2
            else:
                # 1676          E9FA7F77         ADCB    0:95F1,PCR
                raise NotImplementedError,"Adressing-Mode: '%s'" % xb[1]    # CALL b,sp 06
        elif mode == EX:
            if isBitFunction(mnemonic):
                # 0x56BF 1C -- BSET $2087   // 0x56BF   1C208707      BSET    2087 #07
                operand = '$%04X #$%02X' % ((data.getByte(pc + 1) << 8) | data.getByte(pc + 2), data.getByte(pc + 3))
            elif isBitBranchFunction(mnemonic):
                pass
            else:
                operand = '$%04X' % ((data.getByte(pc + 1) << 8) | data.getByte(pc + 2),)
        elif mode == RL:
            if op == LOOP:
                try:
                    lb = LB[data.getByte(pc + 1)] # DBNE    Y,467B     0436FC
                    rel = data.getByte(pc + 2)
                    if rel >= 0x80: # todo: Factor out!!!
                        rel = -((~rel & 0xff) + 1)
                    operand = "%s,$%04X" % (lb[1], (pc + 2 + rel))
                    mnemonic = lb[0]
                except:
                    mnemonic = "TRAP"
                    operand = "($%02x $%02x)" % (op, data.getByte(pc + 1))
            else:
                rel = data.getByte(pc + 1)
                if rel >= 0x80: # todo: Factor out!!!
                    rel = -((~rel & 0xff) + 1)
                operand = "0x%04X" % (pc + 2 + rel)
        elif mode == SPECIAL:
            pass
        elif mode == DI:
            operand = '$%02X' % (data.getByte(pc + 1))
        elif isinstance(mode, basestring):
            if mode == 'im-id':
                xb = XB[data.getByte(pc + 2)]
                if size == 4:
                    operand = "#$%02X %s" % ((data.getByte(pc + 3)), xb[0])
                elif size == 5:
                    operand = "#$%04X %s" % (((data.getByte(pc + 3) << 8) | (data.getByte(pc + 4))), xb[0])
                else:
                    raise NotImplementedError
            elif mode == 'ex-id':
                xb = XB[data.getByte(pc + 2)]
                operand = "$%04X %s" % (((data.getByte(pc + 3) << 8) | data.getByte(pc + 4)), xb[0])
            elif mode == 'id-id':
                xb1 = XB[data.getByte(pc + 2)]
                xb2 = XB[data.getByte(pc + 3)]
                operand = "%s %s" % (xb1[0], xb2[0])
            elif mode == 'im-ex':
                if size == 5:
                    operand = "#$%02X,$%04X" % (data.getByte(pc + 2), (data.getByte(pc + 3) << 8) | (data.getByte(pc + 4)))
                elif size == 6:
                    operand = "#$%04X,$%04X" % (((data.getByte(pc + 2) << 8) |  (data.getByte(pc + 3))), (data.getByte(pc + 4) << 8) | data.getByte(pc + 5))
                else:
                    raise NotImplementedError,"???"
            elif mode == 'ex-ex':
                operand = "$%04X,$%04X" % (((data.getByte(pc + 2) << 8) |  (data.getByte(pc + 3))), (data.getByte(pc + 4) << 8) | (data.getByte(pc + 5)))
            elif mode == 'id-ex':
                xb = XB[data.getByte(pc + 2)]
                operand = "%s $%04X" % (xb[0], ((data.getByte(pc + 3) << 8) | data.getByte(pc + 4)))
            else:
                raise NotImplementedError, "Invalid Addressing Mode."
            lhs, rhs = mode.split('-')
            # print "\t\t%s | %s" % (lhs, rhs)
        else:
            raise NotImplementedError, "Fix me!!!"

        print "0x%04X %02X -- %s\t%s" % (pc, op, mnemonic, operand)
        operand = ''


def main():
    logger = logging.getLogger('pyBDM')
    logger.setLevel(logging.INFO)
    pod = ComPod12(0x0, 38400)
    pod.connect()
    pod.logger.debug('=' * 50)
    pod.logger.debug("STARTING '%s'." % os.path.split(sys.argv[0x0])[0x1])
    pod.logger.debug('=' * 50)
    pod.logger.info("BDM-POD: '%s'." % pod.getPODVersion())
    pod.reset()
#    c.writeX(0xaffe)
    pod.targetHalt()

    resetVec = pod.readWord(0xfffe)

    memory = CachedMemory(pod.readArea)

    pod.writePC(resetVec)
#    pod.targetGo()

    #disasm(resetVec, memory)
    disasm(16386, memory)


    pod.close()

if __name__=='__main__':
    main()


