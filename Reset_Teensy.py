#!/usr/bin/python3
########################
# RPi Weather Station
# Adam Hedley
# March 2018
# Reset Teensy
########################
#
# Connection issues with the Teensy sometimes require a rest 
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

  GPIO.output(RST_pin, 0)
  print (" ")
  print ("Resetting...")
  print (" ")
  time.sleep(2)
  GPIO.output(RST_pin, 1)
  time.sleep(10)

  import serial

  print(" ")
  print("Closing AMA0")
  print(" ")
  ser = serial.Serial('/dev/ttyAMA0',9600, timeout=1)
  ser.close
  print("Closing USB by=id")
  print(" ")
  ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
  ser.close
  time.sleep(1)
  print("Closing ACM0")
  print(" ")
  ser = serial.Serial('/dev/ttyACM0',9600, timeout=1)
  ser.close

  print("Open serial port by-id")
  print(" ")
  ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
  print("Serial:  ",ser)
  print(" ")


  # Read serial to confirm
  print("Reading Teensy Serial Data")
  print(" ")
  ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
  read_serial = ser.readline()
  print(read_serial)
  time.sleep(2)
  ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
  read_serial = ser
  print(read_serial)
  time.sleep(2)
  print(read_serial)
  print(" ")
  time.sleep(2)
  ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
  read_serial = ser
  print(read_serial)
  time.sleep(2)
  print(read_serial)
  print(" ")
  time.sleep(2)
  ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
  read_serial = ser
  print(read_serial)
  time.sleep(2)
  print(read_serial)
  print(" ")

  print ("Reset complete")
  print (" ")
  ser.close

  exit()

if __name__ == "__main__":

    main()

