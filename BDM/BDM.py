#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

abstractmethod=abc.abstractmethod

class Device(object):
    __metaclass__=abc.ABCMeta
    DEVICE_NAME=None

    @abstractmethod
    def Reset(self):                    pass
    @abstractmethod
    def TargetGo(self):                 pass
    @abstractmethod
    def TargetTagGo(self):              pass
    @abstractmethod
    def TargetHalt(self):               pass
    @abstractmethod
    def TargetTrace(self):              pass

    @abstractmethod
    def ReadBDWORD(self,addr):          pass
    @abstractmethod
    def ReadWORD(self):                 pass
    @abstractmethod
    def WriteBDWord(self,addr,data):    pass
    @abstractmethod
    def WriteWord(self,addr,data):      pass
    @abstractmethod
    def ReadNext(self):                 pass
    @abstractmethod
    def WriteNext(self,data):           pass
    @abstractmethod
    def ReadPC(self):                   pass
    @abstractmethod
    def ReadD(self):                    pass
    @abstractmethod
    def ReadX(self):                    pass
    @abstractmethod
    def ReadY(self):                    pass
    @abstractmethod
    def ReadSP(self):                   pass
    @abstractmethod
    def ReadCCR(self):                  pass

    @abstractmethod
    def WritePC(self,data):             pass
    @abstractmethod
    def WriteD(self,data):              pass
    @abstractmethod
    def WriteX(self,data):              pass
    @abstractmethod
    def WriteY(self,data):              pass
    @abstractmethod
    def WriteSP(self,data):             pass
    @abstractmethod
    def WriteCCR(self,data):            pass
