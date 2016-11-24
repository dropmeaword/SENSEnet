# -*- coding: utf8 -*-
import importlib
import logging

__author__ = "Luis Rodil-Fernandez <root@derfunke.net>"
__version__ = "0.2b"

class Inlet(object):
    """ Input data procesing port """
    def __init__(self, root, name):
        self.packets = 0
        self.root = root
        self.name = name

    def pump(self, out):
        self.packets += 1
        return out

    def flush(self):
        pass

    def work(self, data):
        pass

class Outlet(object):
    """ Output data processing port """
    def __init__(self, root, name):
        self.packets = 0
        self.root = root
        self.name = name

    def pump(self, out):
        self.packets += 1
        return out

    def flush(self):
        pass

    def work(self):
        pass
