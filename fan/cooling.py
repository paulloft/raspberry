#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import sys

######################### [Configuration] ##############################################
FAN_PIN = 24            # BCM pin used to drive transistor's base
WAIT_TIME = 1           # [s] Time to wait between each refresh
TEMP_MIN = 45           # [C] The temperature in Celsius after which we trigger the fan
TEMP_MAX = 50           # [C] Temp when we turn the fan off
########################################################################################

fanRunning = False

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    return()

def getCPUtemperature():
    # Read CPU temperature
    cpuTempFile = open('/sys/class/thermal/thermal_zone0/temp', 'r')
    temp = float(cpuTempFile.read()) / 1000
    cpuTempFile.close()

    return temp

def fanON():
    GPIO.output(FAN_PIN, True)
    return()

def fanOFF():
    GPIO.output(FAN_PIN, False)
    return()

def checkTemp():
    global fanRunning
    temperature = getCPUtemperature()

    if (not fanRunning and temperature > TEMP_MAX):
        fanRunning = True
        fanON()

    if (fanRunning and temperature <  TEMP_MIN):
        fanRunning = False
        fanOFF()

    return()

try:
    setup() 
    while True:
        checkTemp()
        time.sleep(WAIT_TIME)

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt 
    GPIO.cleanup() # resets all GPIO ports used by this program