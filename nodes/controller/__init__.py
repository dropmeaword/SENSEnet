# -*- coding: utf8 -*-
import importlib
import logging
import sys

class AbstractController(object):
    """ Abstract controller is the parent class for all controller types """
    def __init__(self, _id):
        self.id = _id
        self.inlets = []
        self.outlets = []

    def update(self):
        packets_in = 0
        packets_out = 0
        for inlet in self.inlets:
            data = inlet.work()
            packets_in += inlet.packets
            if data:
                for outlet in self.outlets:
                    outlet.work(data)
                    packets_out += outlet.packets

        sys.stdout.write("In: {0}      Out: {1}\r".format(packets_in, packets_out))


    def append_inlet(self, callback):
        if callback in self.inlets:
            logging.warning("Trying to append an inlet that already existed " % callback)
        else:
            self.inlets.append(callback)

    def append_outlet(self, callback):
        if callback in self.outlets:
            logging.warning("Trying to append an outlet that already existed " % callback)
        else:
            self.outlets.append(callback)


def create_controller(klass):
    """ create an instance to interface with a particular interface """
    _klass = getattr(importlib.import_module("nodes.controller"), klass)
    instance = _klass()
    return instance
