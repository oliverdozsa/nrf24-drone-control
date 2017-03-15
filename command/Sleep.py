# -*- coding: utf-8 -*-

"""
@author: Oliver Dozsa
"""

import time
from Drone import DroneCommand


class SleepResponse:
    def __init__(self):
        pass

    def process(self, drone_control, data):
        pass


class SleepCommand(DroneCommand):
    def __init__(self, sleep_time):
        super(SleepCommand, self).__init__()

        self.sleep_time = sleep_time

    def execute(self, drone_control, arduino):
        print "Sleeping " + str(self.sleep_time) + " secs..."
        time.sleep(self.sleep_time)

    @property
    def response(self):
        return SleepResponse()

    def __repr__(self):
        return "SL"
