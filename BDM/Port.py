#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc

abstractmethod=abc.abstractmethod

class Port(object):
    MAX_PAYLOAD=None

    @abstractmethod
    def write(self,data):   pass
    @abstractmethod
    def read(self,len):     pass
