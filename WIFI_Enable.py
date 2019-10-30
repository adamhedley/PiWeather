#!/usr/bin/python3
########################
# RPi Weather Station
# Adam Hedley
# November 2018
#
# Enable / Disable WIFI
# from DIO pin to save power
# NOT USING
########################

import os
import time
import datetime
import RPi.GPIO as GPIO

en_pin = 19
enable = 1

# GPIO pin numbering mode
GPIO.setmode(GPIO.BOARD)
# Ignore warnings
GPIO.setwarnings(False)
# Setup GPIO pin as input and add pull-up to default WIFI Enabled
GPIO.setup(en_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# Setup event detection on rising and falling edge
GPIO.add_event_detect(en_pin, GPIO.BOTH)

def main():

  print("WIFI Script Running...")

  while True:

    if GPIO.event_detected(en_pin):

      enable = GPIO.input(en_pin)

      # Enable WIFI
      if enable == 1:
        print(" ")
        print("WIFI ENABLED")
        cmd = 'ifconfig wlan0 up'
        os.system(cmd)
        time.sleep(30)
      else:
      # Disable WIFI
        print(" ")
        print("WIFI DISABLED")
        cmd = 'ifconfig wlan0 down'
        os.system(cmd)
        time.sleep(30)


if __name__=="__main__":
		main()
