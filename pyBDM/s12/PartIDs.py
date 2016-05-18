#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__="0.1.0"

__copyright__="""
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


IDs = {
    0x0010 : (("MC9S12DP256"),      "0K79X"),
    0x0011 : (("MC9S12DP256"),      "1K79X"),
    0x0012 : (("MC9S12DP256"),      "2K79X"),
    0x0030 : (("MC9S12DT256"),      "0L91N"),

    0x0100 : (("MC9S12DT128B"),     "0L85D"),
    0x0101 : (("MC9S12DT128B"),     "1L85D"),
    0x0110 : (("MC9S12DT128"),      "0L94R"),
    0x0111 : (("MC9S12DT128"),      "1L40K"),
    0x0113 : (("MC9S12DT128"),      "3L40K"),
    0x0114 : (("MC9S12DT128"),      "4L40K"),

    0x0115 : (("MC9S12DT128"),      ("1L59W","5L40K","2L94R")),

    0x0200 : (("MC9S12DJ64"),       "0L86D"),
    0x0201 : (("MC9S12DJ64"),       ("1L86D","2L86D")),
    0x0203 : (("MC9S12DJ64"),       "3L86D"),
    0x0204 : (("MC9S12DJ64"),       "4L86D"),

    0x0400 : (("MC9S12DP512"),      "0L00M"),
    0x0401 : (("MC9S12DP512"),      "1L00M"),
    0x0402 : (("MC9S12DP512"),      "2L00M"),
    0x0403 : (("MC9S12DP512"),      "3L00M"),
    0x0404 : (("MC9S12DP512"),      "4L00M"),

    0x0682 : (("MC3S12RG128"),      "2M38B"),

    0x1000 : (("MC9S12H256"),       "0K78X"),
    0x1001 : (("MC9S12H256"),       "1K78X"),

    0x1402 : (("MC9S12HZ256"),      "2L16Y"),
    0x1403 : (("MC9S12HZ256"),      "3L16Y"),


    0x1501 : (("MC3S12HN32","MC9S12HN64",
        "MC3S12HZ32","MC3S12HZ64","MC3S12HZ128",
        "MC3S12HZ256"),             "1M36C"),

    0x1A80 : (("MC9S12HY32","MC9S12HY48",
        "MC9S12HY64","MC9S12HA32","MC9S12HA48",
        "MC9S12HA64"),              "0M34S"),

    0x3102 : (("MC9S12C64","MC9S12C96",
        "MC9S12C128","MC9S12GC64","MC9S12GC96",
        "MC9S12GC128","MC9S12Q64", "MC9S12Q96",
        "MC9S12Q128"),              "2L09S"),

    0x3103 : (("MC9S12C64","MC9S12C96",
        "MC9S12C128","MC9S12GC64","MC9S12GC96",
        "MC9S12GC128","MC9S12Q64","MC9S12Q96",
        "MC9S12Q128"),              "0M66G"),
    0x3300 : (("MC9S12C32"),        "1L45J"),

    0x3302 : (("MC9S12C32","MC9S12GC16",
        "MC9S12GC32","MC9S12Q32"),  "2L45J"),

    0x3310 : (("MC9S12C32",
        "MC9S12GC32"),              "0M34C"),

    0x3311 : (("MC9S12C32","MC9S12GC32",
        "MC3S12Q32"),               "1M34C"),

    0x3980 : (("MC9S12P32","MC9S12P64",
        "MC9S12P96","MC9S12P128"),  "0M01N"),

    0x5000 : (("MC9S12E256"),       "0L43X"),
    0x5102 : (("MC9S12E128"),       "2L15P"),

    0x5200 : (("MC9S12E64"),        "2L15P"),
#    0x5300 : (("MC9S12E32"),        "TBD"),
    0x6300 : (("MC9S12UF32"),       ("0L24N","1L79R")),
    0x6310 : (("MC9S12UF32"),       "0L47S"),
    0x6311 : (("MC9S12UF32"),       "1L47S"),
    0x7000 : (("MC9S12KT256"),      "0L33V"),
    0x7100 : (("MC9S12KG128"),      "0L74N"),
    0x8200 : (("MC9S12NE64"),       "0L19S"),
    0x8201 : (("MC9S12NE64"),       "1L19S"),
    0xC000 : (("MC9S12XDQ256", "MC9S12XDT256", "MC9S12XDT256",
               "MC9S12XB256"),      "M84E"),

    0xC080 : (("MC9S12XET256"),     "0M53J"),
    0xC081 : (("MC9S12XEA128", "MC9S12XEA256", "MC9S12XEG128",
               "MC9S12XET256"),            "1M53J"),

    0xC410 : (("MC9S12XDT384", "MC9S12XDP512"),
                                    "L15Y"),

    0xC480 : (("MC9S12XEQ512"),     "0M25J"),
    0xC481 : (("MC9S12XEQ512"),     "1M25J"),

    0xC482 : (("MC9S12XEG384","MC9S12XEQ384",
        "MC9S12XEQ512",
        "MC9S12XES384"),            "2M25J"),
############################

    0xCC80 : (("MC9S12XEP100"),     ("1M22E","0M22E")),
    0xCC82 : (("MC9S12XEP100"),     "2M22E"),
    0xCC90 : (("MC9S12XEP100"),     "0M48H"),
    0xCC91 : (("MC9S12XEP100"),     "1M48H"),
    0xCC92 : (("MC9S12XEP100"),     "2M48H"),
    0xCC93 : (("MC9S12XEP100"),     "3M48H"),
    0xCC94 : (("MC9S12XEP768",
        "MC9S12XEP100"),            "4M48H"),

    0xD480 : (("MC9S12XF512"),      "0M64J"),

}

'''
MC9S12XDP512    0L15Y/1L15Y         0xC410/0xC411
MC9S12XDT512    0L15Y/1L15Y         0xC410/0xC411
MC9S12XA512     0L15Y/1L15Y         0xC410/0xC411
MC9S12XDT384    0L15Y/1L15Y         0xC410/0xC411
MC9S12XDQ256    0L15Y/1L15Y         0xC410/0xC411
MC9S12XDT256    0L15Y/1L15Y         0xC410/0xC411
MC9S12XD256     0L15Y/1L15Y         0xC410/0xC411
MC9S12XB256     0L15Y/1L15Y         0xC410/0xC411
MC9S12XA256     0L15Y/1L15Y         0xC410/0xC411
MC9S12XDG128    0L15Y/1L15Y         0xC410/0xC411
                0M42E/1M42E         0xC100/0xC101
MC9S12XD128     0L15Y/1L15Y         0xC410/0xC411
                0M42E/1M42E         0xC100/0xC101
MC9S12XA128     0L15Y/1L15Y         0xC410/0xC411
                0M42E/1M42E         0xC100/0xC101
MC9S12XB128     0L15Y/1L15Y         0xC410/0xC411
                0M42E/1M42E         0xC100/0xC101
'''

"""
PARTIDH and PARTIDL (addresses 0x001A and 0x001B)

NOTES:
1. The coding is as follows:
Bit 15-12: Major family identifier
Bit 11-8: Minor family identifier
Bit 7-4: Major mask set revision number including FAB transfers
Bit 3-0: Minor - non full - mask set revision

/*
The PRTIDH register is constructed of four hexadecimal digits (0xABCD) as follows:

Digit “A” = Family ID
Digit “B” = Memory ID (flash size)
Digit “C” = Major mask revision
Digit “D” = Minor mask revision

Currently, family IDs are:
0x0 = D family
0x1 = H family
0x2 = B family
0x3 = C family
0x4 = T family
0x5 = E family
0x6 = reserved  - U
0x7 = reserved  - K
0x8 = NE family

0xC = XE - ???
0xD = XF

Current memory IDs are:
0x0 = 256K
0x1 = 128K
0x2 = 64K
0x3 = 32K
0x4 = 512K
*/
"""

