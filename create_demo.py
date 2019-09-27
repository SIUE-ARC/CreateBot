#!/usr/bin/env python3
import time
import create
import numpy as np
robot = create.Create("/dev/ttyUSB0")


command = ''
print("Robot initialized!")
while(1):
    command = input()
    if(command == 'q'): #Quit
        exit(1)
    elif(command == 'r'): #Drive
        velocity = np.int16(input("Input velocity and radius.\nVelocity (-500 - 500)mm/s:   "))
        radius   = np.int16(input("Radius (-2000 - 2000)mm:   "))
        robot.drive(velocity,radius)
    elif(command == 'd'): #Direct Drive
        RWheel = np.int16(input("Input wheel velocities for R and L. \nRight Wheel (-500 - 500)mm/s: "))
        LWheel = np.int16(input("Left Wheel (-500 - 500)mm/s: "))
        robot.drive_direct(RWheel,LWheel)
    elif(command == 'l'): #Control LEDs
        Play = np.int16(input("Input LED Values. \nPlay (0-1): "))
        Advance = np.int16(input("Advance (0-1): "))
        if(Play):
            Play = 1
        else:
            Play = 0
        if(Advance):
            Advance = 1
        else:
            Advance = 0
        robot.leds(Play,Advance)
    elif(command == 's'): #Stop Movement
        print("MAYDAY MAYDAY MAYDAY")
        robot.drive_direct(0,0);
    elif(command == 'a'): #Check Sensors
        robot.sensor_print_all()
    elif(command == 'm'): #Change Mode
        mode = input("Input mode to switch to (S, F, P):\t")
        if(mode in ['s','S']):
            robot.safe_mode()
        elif(mode in ['f','F']):
            robot.full_mode()
        elif(mode in ['p','P']):
            robot.passive_mode()
        else:
            print("Invalid Input, No mode change\n")
