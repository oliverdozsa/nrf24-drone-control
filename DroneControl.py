# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 12:10:27 2017

@author: Oliver Dozsa

license: MIT
"""

import serial
import time
import threading
import msvcrt
from command.Drone import DroneCommand
from command.DroneSequence import Actions
from command.DroneSequence import DroneSequenceCommand
from command.Sleep import SleepCommand
from command.DroneSequence import LAND_SEQ
from command.DroneSequence import LIFTOFF_SEQ
import traceback
import sys


class DroneControl(threading.Thread):

    def __process_response(self, data):
        if "selecting protocol" in data:
            self.__isReady = False
            self.__isProcessing = True
            return
        if "init protocol complete" in data:
            print "[PC]: Waiting to establish signal..."
            time.sleep(15)
            print "[PC]: done!"
            self.__isReady = True
            self.__isProcessing = False
            return

        if self.__commandsQ and self.__commandsQ[0]:
            command = self.__commandsQ[0]
            command.response.process(self, data)
            self.__isProcessing = False
            del self.__commandsQ[0]
            if not self.__commandsQ:
                print "Q: []"

    def __read_response(self):
        data = self.arduino.readline()

        is_process = False
        proc_data = ""

        if data:
            print "[PC] <- [AU]: " + data
            is_process = True
            proc_data = data
        elif self.__commandsQ:
            act_cmd = self.__commandsQ[0]
            if isinstance(act_cmd, DroneSequenceCommand) or \
                    isinstance(act_cmd, SleepCommand):
                if act_cmd.is_executing:
                    # They have no answer from Arduino
                    is_process = True

        if is_process:
            self.__process_response(proc_data)

    def __close_control(self):
        # close the connection
        self.arduino.close()
        # re-open the serial port which will also reset the Arduino Uno and
        # this forces the quadcopter to power off when the radio loses
        # conection.
        self.arduino = serial.Serial(self.comPort, 115200, timeout=.01)
        self.arduino.close()
        # close it again so it can be reopened the next time it is run.

    def __control_sequence(self):
        try:
            while True:
                self.__read_response()

                if(not self.__isProcessing and self.__isReady and
                        not len(self.__commandsQ) == 0):
                    print "Q: " + repr(self.__commandsQ)
                    command = self.__commandsQ[0]
                    command.is_executing = True
                    command.execute(self, self.arduino)
                    self.__isProcessing = True

                # TODO: Temporary
                if msvcrt.kbhit():
                    key = ord(msvcrt.getch())
                    if key == 27:  # ESC
                        print "[PC]: ESC exiting"
                        break
        finally:
            self.__close_control()

    def __init__(self, comPort):
        threading.Thread.__init__(self)
        self.comPort = comPort
        self.__isReady = False
        self.__isProcessing = True
        self.__commandsQ = []
        self.arduino = None

    def run(self):
        print "[PC]: Starting up"
        self.arduino = serial.Serial(self.comPort, 115200, timeout=.01)
        time.sleep(1)  # give the connection a second to settle
        self.__control_sequence()

    def execute(self, command):
        # Only accept supported commands
        if isinstance(command, DroneCommand):
            command.is_executing = False
            self.__commandsQ.append(command)
        else:
            raise ValueError("Command is not supported! command = " + command)

    def is_ready(self):
        return self.__isReady

def calib_array_kb(array_in):
    mod_array = array_in
    print "Entering array calib"
    print str(mod_array)
    sys.stdout.flush()
    i = 0

    while True:
        if msvcrt.kbhit():
            key_v = ord(msvcrt.getch())
            if key_v == 120:  # x
                print "Leaving array calib"
                break
            elif key_v == 119:  # w
                mod_array[i] += 10
            elif key_v == 115:  # s
                mod_array[i] -= 10
            elif key_v == 97:  # a
                i = (i-1) % 4
            elif key_v == 100:  # d
                i = (i+1) % 4

            print "\r" + str(mod_array),
            sys.stdout.flush()

    return mod_array

if __name__ == "__main__":
    control = DroneControl("COM3")

    control.start()

    while not control.is_ready():
        pass

    while True:
        try:
            if msvcrt.kbhit():
                key = ord(msvcrt.getch())
                if key == 119:  # w
                    drone_cmd = DroneSequenceCommand(Actions.LIFTOFF, 0.0)
                    control.execute(drone_cmd)
                elif key == 115:  # s
                    drone_cmd = DroneSequenceCommand(Actions.LAND, 0.0)
                    control.execute(drone_cmd)
                elif key == 99:  # c
                    print "Entered calib mode"
                    while True:
                        if msvcrt.kbhit():
                            calib_key = ord(msvcrt.getch())

                            if calib_key == 99:  # c
                                print "Leaving calib mode"
                                break
                            elif calib_key == 114:  # r
                                LIFTOFF_SEQ[0] = calib_array_kb(LIFTOFF_SEQ[0])
                            elif calib_key == 116:  # t
                                LIFTOFF_SEQ[1] = calib_array_kb(LIFTOFF_SEQ[1])
                            elif calib_key == 103:  # g
                                LIFTOFF_SEQ[1][0] -= 10
                                print "LO:" + str(LIFTOFF_SEQ[0])
                                print "LO:" + str(LIFTOFF_SEQ[1])
                elif key == 27:  # ESC
                    break

        except Exception as e:
            traceback.print_exc()
            print "Invalid input! Try again!"
