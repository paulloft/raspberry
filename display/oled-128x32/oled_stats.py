#!/usr/bin/env python

import oled
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont

oled.init()  #initialze SEEED OLED display

oled.clearDisplay()          #clear the screen and set start position to top left corner
oled.setNormalDisplay()      #Set display to normal mode (i.e non-inverse mode)
oled.setHorizontalMode()

width = 128
height = 32

logo = Image.open('friendllyelec.png').convert('1')
oled.drawImage(logo)

image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
offset = -2
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font.
font = ImageFont.load_default()

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
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

    draw.text((x, offset+0), "IP: "+IP, font=font, fill=255)
    draw.text((x, offset+8), CPU + " " + str(TEMP) + "C", font=font, fill=255)
    draw.text((x, offset+16), MemUsage, font=font, fill=255)
    draw.text((x, offset+25), Disk, font=font, fill=255)

    # Display image.
    oled.drawImage(image)
    time.sleep(.1)
