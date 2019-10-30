#!/usr/bin/python3
########################
# RPi Weather Station
# Adam Hedley
# March 2018
# Reset Teensy
########################
#
# Run as a CRON on reboot to make sure Reset Pin to Teensy is correctly set.
#
# GPIO.BOARD – Board numbering scheme. The pin numbers follow the pin numbers on header P1.
# GPIO.BCM – Broadcom chip-specific pin numbers. These pin numbers follow the lower-level numbering
# system defined by the Raspberry Pi’s Broadcom-chip brain.
#
# The GPIO.BOARD option specifies that you are referring to the pins by the number of the pin the the plug -
# i.e the numbers printed on the board (e.g. P1) and in the middle of the diagrams below.
#
# The GPIO.BCM option means that you are referring to the pins by the "Broadcom SOC channel" number, these are the numbers after "GPIO" 

import RPi.GPIO as GPIO
import time
#import serial

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

RST_pin = 7

GPIO.setup(RST_pin, GPIO.OUT)

def main():

  GPIO.output(RST_pin, 1)
  print (" ")
  print ("Reset Set HIGH...")
  print (" ")

  exit()

if __name__ == "__main__":

    main()

