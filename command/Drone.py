# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 21:27:50 2017

@author: Oliver Dozsa
"""


class DroneResponse(object):
    def __init__(self):
        pass

    def process(self, drone_control, data):
        pass


class DroneCommand(object):
    def __init__(self):
        pass

    def execute(self, drone_control, arduino):
        pass

    @property
    def response(self):
        return DroneResponse()
