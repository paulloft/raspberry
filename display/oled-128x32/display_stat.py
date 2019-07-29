#!/usr/bin/env python

import os
import lib.oled as oled 
import time
import subprocess
import traceback
from PIL import Image, ImageDraw, ImageFont
import  NPi.GPIO as GPIO

# Button GPIO pin
PIN_BTN = 7
# Update period
UPDATE_DELAY = .2
# Display Time
DISPLAY_TIME = 5
# Button hold time for off
POWEROFF_TIME = 2

OFFSET = -2
# Move left to right keeping track of the current x position for drawing shapes.
X_POS = 0

WIDTH = oled.SeeedOLED_Width
HEIGHT = oled.SeeedOLED_Height
showTimer = 0
poweroffTimer = 0
isDisplayCleared = False

def setupGPIO():
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    GPIO.setup(PIN_BTN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    return()

def buttonState():
    global showTimer
    global poweroffTimer
    global isDisplayCleared

    inputState = GPIO.input(PIN_BTN)
    if inputState == GPIO.HIGH:
        showTimer = 0
        isDisplayCleared = False
        poweroffTimer += UPDATE_DELAY
    else:
        poweroffTimer = 0

    if (poweroffTimer > POWEROFF_TIME):
        shutdown()

    return()

def shutdown():
    global draw
    global image
    global font

    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    draw.text((48, 15), 'SHUTDOWN', font=font, fill=255)
    oled.drawImage(image)
    time.sleep(1)
    oled.clearDisplay()
    time.sleep(0.5)

    subprocess.check_output('shutdown now', shell=True)
    raise SystemExit

def setupDisplay():

    oled.init()                  #initialze SEEED OLED display
    oled.clearDisplay()          #clear the screen and set start position to top left corner
    oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
    oled.setHorizontalMode()

    dir = os.path.dirname(__file__)
    if dir:
        dir = dir + '/'

    logo = Image.open(dir + 'logo.png').convert('1')
    oled.drawImage(logo)

    return()

def updateStats(image, draw, font):
    global showTimer
    global isDisplayCleared

    showTimer += UPDATE_DELAY

    if showTimer > DISPLAY_TIME:
        if isDisplayCleared == False:
            isDisplayCleared = True
            oled.clearDisplay()
        return -1

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

    cmd = "cat /sys/class/thermal/thermal_zone0/temp"
    TEMP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    TEMP = round(float(TEMP) / 1000, 1)

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "top -bn1 | grep load | awk '{printf \"CPU: %.2f%\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

    # texts = ["IP: "+IP, CPU, MemUsage, Disk ]

    # for i in range(8):
    #     oled.setTextXY(0,i)          #Set the cursor to Xth Page, Yth Column  
    #     oled.putString(texts[i]) #Print the String

    # Write four lines of text.

    draw.text((X_POS, OFFSET + 0), "IP: "+IP, font=font, fill=255)
    draw.text((X_POS, OFFSET + 8), CPU + " " + str(TEMP) + "C", font=font, fill=255)
    draw.text((X_POS, OFFSET + 16), MemUsage, font=font, fill=255)
    draw.text((X_POS, OFFSET + 25), Disk, font=font, fill=255)

    # Display image.
    oled.drawImage(image)
    return()


    
try:
    setupDisplay()
    setupGPIO()

    image = Image.new('1', (WIDTH, HEIGHT))
    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    # Load default font.
    font = ImageFont.load_default()

    while True:
        buttonState()
        updateStats(image, draw, font)
        time.sleep(UPDATE_DELAY)

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    oled.clearDisplay()
    print('exit')

except Exception as err:
    oled.clearDisplay()
    print(traceback.format_exc())
