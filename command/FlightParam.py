# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 20:59:04 2017

@author: Oliver Dozsa
"""
from Drone import DroneCommand


class FlightParamResponse:
    def __init__(self, command):
            self.command = command
            self.throttle = 0
            self.aileron = 0
            self.elevator = 0
            self.rudder = 0

    def process(self, drone_control, data):
        elems = data.split(";")

        if len(elems) == 5:
            self.throttle = int(elems[0])
            self.aileron = int(elems[1])
            self.elevator = int(elems[2])
            self.rudder = int(elems[3])

            if not (self.command.aileron == self.aileron and
                    self.command.elevator == self.elevator and
                    self.command.rudder == self.rudder and
                    self.command.throttle == self.throttle):
                        print "Invalid flight param response!"


class FlightParamCommand(DroneCommand):

    def __init__(self, throttle=1000, aileron=1500, elevator=1500, rudder=1500):
        super(FlightParamCommand, self).__init__()

        self.throttle = throttle
        self.aileron = aileron
        self.elevator = elevator
        self.rudder = rudder

        if self.throttle < 1000:
            self.throttle = 1000
        if self.aileron < 1000:
            self.aileron = 1000
        if self.elevator < 1000:
            self.elevator = 1000
        if self.rudder < 1000:
            self.rudder = 1000

    def execute(self, drone_control, arduino):
        command = "%i,%i,%i,%i" % (self.throttle, self.aileron,
                                   self.elevator, self.rudder)
        print "[PC] -> [AU] (FP): " + command
        arduino.write(command + "\n")

    @property
    def response(self):
        return FlightParamResponse(self)

    def __repr__(self):
        return "FP"
