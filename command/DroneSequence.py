# -*- coding: utf-8 -*-
"""
@author: Oliver Dozsa
"""

from Drone import DroneCommand
from FlightParam import FlightParamCommand
from Sleep import SleepCommand

# Group of five numbers; first four is FlighParam, the 5th is time.
_LIFTOFF_SEQ = [
    [1420, 1500, 1500, 1500, 3],
    [1300, 1500, 1500, 1500, 1]
]

_LAND_SEQ = [
    [1200, 1500, 1500, 1500, 1],
    [1050, 1500, 1500, 1500, 1]
]


class Actions:
    def __init__(self):
        pass

    LIFTOFF = 1
    LAND = 2
    GO_UP = 3
    GO_DOWN = 4


class DroneSequenceResponse:
    def __init__(self):
        pass

    def process(self, drone_control, data):
        pass


class DroneSequenceCommand(DroneCommand):
    def __init__(self, action, act_time):
        super(DroneSequenceCommand, self).__init__()

        self.action = action
        self.act_time = act_time

    def execute(self, drone_control, arduino):
        if self.action == Actions.LIFTOFF:
            for param in _LIFTOFF_SEQ:
                flight_cmd = FlightParamCommand(param[0], param[1], param[2], param[3])
                sleep_cmd = SleepCommand(param[4])

                drone_control.execute(flight_cmd)
                drone_control.execute(sleep_cmd)

    @property
    def response(self):
        return DroneSequenceResponse()

    def __repr__(self):
        return "DS"
