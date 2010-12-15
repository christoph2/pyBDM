#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Port
import serial
import sys
import types


class Port(Port.Port):
    def __init__(self,num,baudrate,bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=0.1):
        self.port=None
        try:
            self.port=serial.Serial(port=num,baudrate=baudrate,bytesize=bytesize,
                parity=parity,stopbits=stopbits,timeout=timeout)
        except serial.SerialException,e:
            print sys.exc_info
            raise e
#        print "OK, openend as '%s' @ %d Bits/Sec." % (self.port.portstr,self.port.baudrate)

    def __del__(self):
        if self.port and self.port.isOpen()==True:
            self.port.close()
#            print "Closed COM-Port."

    def write(self,data):
        if not isinstance(data,(types.ListType,types.TupleType)):
            data=[data]
        self.port.write(bytearray(data))

    def read(self,len):
        data=self.port.read(len)
        return bytearray(data)

    '''
    def __getattr__(self,attr):
        return getattr(self.port,attr)

    def setattr(self,attr,value):
        setattr(self.port,attr,value)
    '''


def main():
    pass

if __name__=='__main__':
    main()
