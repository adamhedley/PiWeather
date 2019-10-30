#!/usr/bin/python3
########################
# RPi Weather Station
# Adam Hedley
# March 2018
#
# Teensy connection drops
# this seems to fix it
# 
########################



import time
import datetime
import os
import RPi.GPIO as GPIO
import serial


print(" ")
print("Teensy Reset pin set-up...")
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

RST_pin = 7
GPIO.setup(RST_pin, GPIO.OUT)

print("Teensy reset in progress...")
print(" ")
GPIO.output(RST_pin,0)
print("Reset Enabled")
time.sleep(2)
GPIO.output(RST_pin,1)
print("Reset HIGH")
print(" ")


print("Teensy setup....")
time.sleep(1)
print("1")
time.sleep(1)
print("2")
time.sleep(1)
print("2")
print(" ")

print("Setting up serial bus...")


print ("*** Setting up serial bus ***")
print (" ")

locations=['/dev/ttyACM0', '/dev/ttyACM1','/dev/ttyACM2', '/dev/ttyACM3',
'/dev/ttyACM4', '/dev/ttyACM5','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2',
'/dev/ttyUSB3', '/dev/ttyUSB4', '/dev/ttyUSB5', '/dev/ttyUSB6',
'/dev/ttyUSB7', '/dev/ttyUSB8', '/dev/ttyUSB9', '/dev/ttyUSB10',
 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
 'com10', 'com11', 'com12', 'com13', 'com14', 'com15', 'com16',
 'com17', 'com18', 'com19', 'com20', 'com21', 'com1', 'end']

for device in locations:
  try:
    #print "Trying...",device
    ser = serial.Serial(device, 2400, timeout = 0)
    break
  except:
  #print "Failed to connect on",device
    if device == 'end':
      print ("Unable to find Serial Port, Please plug in cable or check cable connections.")
      exit()

#ser = serial.Serial('/dev/ttyAMA0',9600, timeout=1)
#ser.close

#ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
#ser.close

#ser = serial.Serial('/dev/ttyACM0',9600, timeout=1)
#ser.close

#ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
read_serial = ser.readline()
print(" ")
print("Initial Reading Serial:   ", read_serial)
ser.close()


# Splits data out read back from Teensy board seperated by ' - '
def split_data(sens_pos, serial_data):
  data_split = serial_data.decode().split(' - ')
  sensor = data_split[sens_pos]
  print ("Split Data   ", sensor) # For checking
  print(" ")
  return sensor


# Read Data off Serial Port from Teensy
def read_data():
  ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
  #ser = serial.Serial('/dev/ttyAMA0',9600, timeout=1)
  #ser = serial.Serial('/dev/ttyACM0',9600) #apparantly don't do this in the loop
  read_serial = ser.readline()
  print("Read Data call serial print  ",read_serial) # For checking
  print(" ")


  print("Closing Serial Port")
  print(" ")

  # Close serial port
  ser.close()


def main():

  i = 10

  while i > 1:

    read_data()
    time.sleep(2)

    i -=1

  exit()


if __name__=="__main__":
		main()
