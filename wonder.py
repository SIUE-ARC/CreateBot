#!/usr/bin/env python3

import numpy as np
import create as cr
import time
import xbox

DRIVE_MAX = 250

robot = cr.Create()             #Initialize robot
joy = xbox.Joystick()           #Initialize joystick

print("Robot initialized")

def stop(robot):
    robot.drive_direct(0, 0)
    time.sleep(0.5)

def forward(robot):
    robot.drive_direct(250, 250)

def backup(robot):
    robot.drive_direct(-250, -250)
    time.sleep(0.5)
    stop(robot)

def turn(robot, dir):
    stop(robot)
    backup(robot)
    if dir == "left":
        robot.drive_direct(-250,250)
    elif dir == "right":
        robot.drive_direct(250,-250)
    time.sleep(1)

def main():
    while(1):
        try:
            forward(robot)
            bumper = robot.sensor_reading("bumper")
            if int(bumper[0]):
                print("Turning Left")
                turn(robot,"left")
            elif int(bumper[1]):
                print("Turning Right")
                turn(robot,"right")
        except KeyboardInterrupt:
            stop(robot)
            print("Exiting")
            break

def manual_control(robot, joy):
    while not joy.Back():
        try:
            R_wheel = round(joy.leftY()*DRIVE_MAX)
            L_wheel = round(joy.leftY()*DRIVE_MAX)
            offset = round(joy.leftX()*DRIVE_MAX)
            if offset < 0:
                if R_wheel >= 0 or L_wheel >= 0:
                    L_wheel -= abs(offset)
                    R_wheel += abs(offset)
                elif R_wheel < 0 or L_wheel < 0:
                    R_wheel -= abs(offset)
                    L_wheel += abs(offset)
            elif offset > 0:
                if R_wheel >= 0 or L_wheel >= 0:
                    R_wheel -= abs(offset)
                    L_wheel += abs(offset)
                elif R_wheel < 0 or L_wheel < 0:
                    L_wheel -= abs(offset)
                    R_wheel += abs(offset)
            robot.drive_direct(R_wheel,L_wheel)
        except KeyboardInterrupt:
            stop(robot)
            print("Exiting")
            break

manual_control(robot, joy)
