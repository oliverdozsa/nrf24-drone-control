# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 12:10:27 2017

@author: Oliver Dozsa

license: GPL
"""

import serial
import time
import threading
import msvcrt
from command.Drone import DroneCommand
from command.FlightParam import FlightParamCommand


class DroneControl(threading.Thread):

    def __processResponse(self, data):
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

    def __readResponse(self):
        data = self.arduino.readline()

        if data:
            print "[PC] <- [AU]: " + data
            self.__processResponse(data)

    def __closeControl(self):
        # close the connection
        self.arduino.close()
        # re-open the serial port which will also reset the Arduino Uno and
        # this forces the quadcopter to power off when the radio loses
        # conection.
        self.arduino = serial.Serial(self.comPort, 115200, timeout=.01)
        self.arduino.close()
        # close it again so it can be reopened the next time it is run.

    def __controlSequence(self):
        try:
            while True:
                self.__readResponse()

                if(not self.__isProcessing and self.__isReady and
                        not len(self.__commandsQ) == 0):
                    print "Q: " + repr(self.__commandsQ)
                    command = self.__commandsQ[0]
                    command.execute(self, self.arduino)
                    self.__isProcessing = True

                # TODO: Temporary
                if msvcrt.kbhit():
                    key = ord(msvcrt.getch())
                    if key == 27:  # ESC
                        print "[PC]: ESC exiting"
                        break
        finally:
            self.__closeControl()

    def __init__(self, comPort):
        threading.Thread.__init__(self)
        self.comPort = comPort
        self.__isReady = False
        self.__isProcessing = True
        self.__commandsQ = []

    def run(self):
        print "[PC]: Starting up"
        self.arduino = serial.Serial(self.comPort, 115200, timeout=.01)
        time.sleep(1)  # give the connection a second to settle
        self.__controlSequence()

    def execute(self, command):
        # Only accept supported commands
        if isinstance(command, DroneCommand):
            self.__commandsQ.append(command)
        else:
            raise ValueError("Command is not supported! command = " + command)

    def isReady(self):
        return self.__isReady


if __name__ == "__main__":
    control = DroneControl("COM5")

    control.start()

    while not control.isReady():
        pass

    while True:
        try:
            kinput = raw_input("CMD:")
            if "exit" in kinput:
                print "Exiting"
                break

            elif "read" in kinput:
                f = open("drone_commands.txt", "r")
                j = 0
                cmd = None
                waitTime = 0.0

                for line in f:
                    if j % 2 == 0:
                        cmdParams = line.split(",")
                        cmd = FlightParamCommand(int(cmdParams[0]))
                        j += 1
                    else:
                        waitTime = float(line)
                        control.execute(cmd)
                        time.sleep(waitTime)
                        j = 0
        except:
            print "Invalid input! Try again!"
