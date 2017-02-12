# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 21:27:50 2017

@author: Oliver Dozsa
"""


class DroneResponse:
    def process(self, drone_control, data):
        pass


class DroneCommand:
    def execute(self, drone_control, arduino):
        pass

    @property
    def response(self):
        pass
