#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BDM
import Serial

from BDM import Device
from Port import Port

##
##  BMD-Commands.
##

# *** Elektronik-Laden ***
RESET           = 0x80 # Reset
FILL_AREA       = 0x82 # FILL_AREA ADDR_HI ADDR_LO CNT DATA
READ_AREA       = 0x83 # READ_AREA ADDR_HI ADDR_LO CNT (0==0xff)
VERSION         = 0xFF


#END-*** Elektronik-Laden ***

BACKGROUND      = 0x90 # Enter background mode if firmware enabled.
READ_BD_BYTE    = 0xE4 # Read from memory with BDM in map.
READ_BD_WORD    = 0xEC # Read from memory with BDM in map.
READ_BYTE       = 0xE0 # Read from memory with BDM out of map.
READ_WORD       = 0xE8 # Read from memory with BDM out of map.
WRITE_BD_BYTE   = 0xC4 # Write to memory with BDM in map.
WRITE_BD_WORD   = 0xCC # Write to memory with BDM in map.
WRITE_BYTE      = 0xC0 # Write to memory with BDM out of map.
WRITE_WORD      = 0xC8 # Write to memory with BDM out of map.
READ_NEXT       = 0x62 # X = X + 2; Read next word pointed to by X
READ_PC         = 0x63 # Read program counter.
READ_D          = 0x64 # Read D accumulator.
READ_X          = 0x65 # Read X index register.
READ_Y          = 0x66 # Read Y index register.
READ_SP         = 0x67 # Read stack pointer.
WRITE_NEXT      = 0x42 # X = X + 2; Write next word pointed to by X
WRITE_PC        = 0x43 # Write program counter.
WRITE_D         = 0x44 # Write D accumulator.
WRITE_X         = 0x45 # Write X index register.
WRITE_Y         = 0x46 # Write Y index register.
WRITE_SP        = 0x47 # Write stack pointer.
GO              = 0x08 # Go to user program.
TRACE1          = 0x10 # Execute one user instruction then return to BDM.
TAGGO           = 0x18 # Enable tagging and go to user program.


class NoResponseError(Exception): pass
class InvalidResponseError(Exception): pass

def com(v):
    return 0xff & ~v

class ComPod12(Device,Serial.Port):
    MAX_PAYLOAD=0xff
    DEVICE_NAME="Elektronik-Laden ComPOD12"

    def __writeCommand__(self,cmd,responseLen):
        self.write(cmd)
        data=self.read(responseLen)
        if data==bytearray():
            raise NoResponseError
        if data[0]!=com(cmd):
            raise InvalidResponseError
        if len(data)>1:
            return data[1:]
        else:
            return None

    def __readCommand__(self,cmd,responseLen,addr=None):
        self.write(cmd)
        if not addr is None:
            self.write((addr>>8) & 0xff)
            self.write(addr & 0xff)
        data=self.read(responseLen)
        if data==bytearray():
            raise NoResponseError
        if len(data)!=responseLen:
            raise InvalidResponseError
        return data
    
    def __readWord__(self,cmd,addr=None):
        data=self.__readCommand__(cmd,2,addr)
        if data==bytearray():
            raise NoResponseError
        if len(data)!=2:
            raise InvalidResponseError
        return data[0]<<8 | data[1]

    def __writeWord__(self,cmd,data0,data1=None):
        self.write(cmd)
        self.write((data0>>8) & 0xff)
        self.write(data0 & 0xff)
        if data1:
            self.write((data1>>8) & 0xff)
            self.write(data1 & 0xff)
        d=self.read(1)
        if d==bytearray():
            raise NoResponseError
        if (d[0]!=com(cmd)):
            raise InvalidResponseError

    def __writeByte__(self,cmd,addr,data):
        self.write(cmd)
        self.write((addr>>8) & 0xff)
        self.write(addr & 0xff)
        self.write(data)
        d=self.read(1)
        if d==bytearray():
            raise NoResponseError
        if (d[0]!=com(cmd)):
            raise InvalidResponseError

    def Reset(self):
        self.__writeCommand__(RESET,1)

    def getPODVersion(self):
        data=self.__readCommand__(VERSION,2)
        return "%s v%02u.%02u" % (self.DEVICE_NAME,data[0],data[1])

    def TargetGo(self):
        self.__writeCommand__(GO,1)

    def TargetTagGo(self):
        self.__writeCommand__(TAGGO,1)

    def TargetHalt(self):
        self.__writeCommand__(BACKGROUND,1)

    def TargetTrace(self):
        self.__writeCommand__(TRACE1,1)

    def ReadBDWORD(self,addr):
        return self.__readWord__(READ_BD_WORD,addr)

    def ReadWORD(self,addr):
        return self.__readWord__(READ_WORD,addr)

    def ReadBDByte(self,addr):
        data=self.__readCommand__(READ_BD_BYTE,1,addr)
        return data[0]

    def ReadByte(self,addr):
        data=self.__readCommand__(READ_BYTE,1,addr)
        return data[0]

    def ReadNext(self):
        return self.__readWord__(READ_NEXT)

    def ReadPC(self):
        return self.__readWord__(READ_PC)

    def ReadD(self):
        return self.__readWord__(READ_D)

    def ReadX(self):
        return self.__readWord__(READ_X)

    def ReadY(self):
        return self.__readWord__(READ_Y)
        
    def ReadSP(self):
        return self.__readWord__(READ_SP)

    def ReadCCR(self):
        return self.ReadBDByte(0xff06)

    def WritePC(self,data):
        self.__writeWord__(WRITE_PC,data)

    def WriteD(self,data):
        self.__writeWord__(WRITE_D,data)

    def WriteX(self,data):
        self.__writeWord__(WRITE_X,data)

    def WriteY(self,data):
        self.__writeWord__(WRITE_Y,data)

    def WriteSP(self,data):
        self.__writeWord__(WRITE_SP,data)

    def WriteCCR(self,data):
        return self.WriteBDByte(0xff06,data)

    def WriteBDWord(self,addr,data):
        self.__writeWord__(WRITE_BD_WORD,addr,data)

    def WriteWord(self,addr,data):
        self.__writeWord__(WRITE_WORD,addr,data)

    def WriteBDByte(self,addr,data):
        self.__writeByte__(WRITE_BD_BYTE,addr,data)

    def WriteByte(self,addr,data):
        self.__writeByte__(WRITE_BYTE,addr,data)

    def WriteNext(self,data):
        self.__writeWord__(WRITE_NEXT,data)


c=ComPod12(0,38400)
print c.getPODVersion()
c.Reset()
c.TargetHalt()
#c.TargetTrace()

c.WritePC(0x4712)
c.WriteX(0xdead)
c.WriteY(0xaffe)

c.WriteByte(0x1000,0x33)
c.WriteByte(0x1001,0x44)
c.WriteByte(0x1002,0x55)
c.WriteByte(0x1003,0x66)

print hex(c.ReadWORD(0xFFFe))

print hex(c.ReadWORD(0x1000)),hex(c.ReadWORD(0x1002))

print hex(c.ReadByte(0x1001))
print hex(c.ReadByte(0x1002))
print hex(c.ReadByte(0x1003))

print hex(c.ReadPC())
print hex(c.ReadSP())
print hex(c.ReadD())
print hex(c.ReadX())
print hex(c.ReadY())
print hex(c.ReadCCR())
