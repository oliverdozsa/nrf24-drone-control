# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 12:10:27 2017

@author: Oliver Dozsa

license: GPL
"""

import serial, time, msvcrt, threading

class FlightParamCommand:
    
    def __init__(self, throttle = 1000, aileron = 1500, elevator = 1500, rudder = 1500):
        self.throttle = throttle
        self.aileron = aileron
        self.elevator = elevator
        self.rudder = rudder
        
        if self.throttle < 1000:
            self.throttle = 1000
        if self.aileron < 1500:
            self.aileron = 1500
        if self.elevator < 1500:
            self.elevator = 1500
        if self.rudder < 1500:
            self.rudder = 1500
    
    def __repr__(self):
        return "FP"
 
class _FlightParamResponse:
    def __init__(self, data):
        self.isValid = False
        
        elems = data.split(";")
        
        if len(elems) == 5:
            self.throttle = int(elems[0])
            self.aileron = int(elems[1])
            self.elevator = int(elems[2])
            self.rudder = int(elems[3])
            
            self.isValid = True
        
    def verify(self, command):        
        result = False
        if isinstance(command, FlightParamCommand):
            if command.aileron == self.aileron and command.elevator == self.elevator and command.rudder == self.rudder and command.throttle == self.throttle:
                result = True
        return result
    

class DroneControl(threading.Thread):
    
    def __sendFlightParams(self, throttle, aileron, elevator, rudder):
        command = "%i,%i,%i,%i"% (throttle, aileron, elevator, rudder)
        
        print "[PC] -> [AU] (FP): " + command
        
        self.arduino.write(command + "\n")
        
        
    def __processResponse(self, data):
        if "selecting protocol" in data:
            self.__isReady = False
            self.__isProcessing = True
            return
        if "init protocol complete" in data:
            self.__isReady = True
            self.__isProcessing = False
            return
        
        # identify response
        resp = _FlightParamResponse(data)
        if resp.isValid:
            if resp.verify(self.__commandsQ[0]):
                self.__isProcessing = False
                del self.__commandsQ[0]
                if not self.__commandsQ:
                    print "Q: []"
            else:
                print "Response not verified!"
            
    
    def __readResponse(self):
        data = self.arduino.readline()
        
        if data:
            print "[PC] <- [AU]: " + data
            self.__processResponse(data)
            
    
    def __closeControl(self):
        # close the connection
        self.arduino.close()
        # re-open the serial port which will also reset the Arduino Uno and
        # this forces the quadcopter to power off when the radio loses conection. 
        self.arduino=serial.Serial(self.comPort, 115200, timeout = .01)
        self.arduino.close()
        # close it again so it can be reopened the next time it is run. 
        
        
    def __controlSequence(self):
        
        try:
            while True:
                self.__readResponse()
                
                if(not self.__isProcessing and self.__isReady and not len(self.__commandsQ) == 0):
                    print "Q: " + repr(self.__commandsQ)
                    command = self.__commandsQ[0]
                    if isinstance(command, FlightParamCommand):
                        self.__sendFlightParams(command.throttle, command.aileron, command.elevator, command.rudder)
                        self.__isProcessing = True
                
                if msvcrt.kbhit():
                    key = ord(msvcrt.getch())
                    
                    if key == 27: #ESC
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
        print "run()"
        
        self.arduino = serial.Serial(self.comPort, 115200, timeout = .01)
        time.sleep(1) #give the connection a second to settle
        
        self.__controlSequence()
        
        
    def execute(self, command):
        # Only accept supported commands
        if isinstance(command, FlightParamCommand):            
            self.__commandsQ.append(command)
        else:
            raise ValueError("Command is not supported! command = " + command)    


if __name__ == "__main__":
    control = DroneControl("COM3")
    
    control.start()
    
    for i in [0, 10, 20, 30, 40, 50, 60, 70]:
        cmd = FlightParamCommand(1000 + i)
        control.execute(cmd)
    