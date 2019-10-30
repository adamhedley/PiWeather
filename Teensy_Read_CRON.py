#!/usr/bin/python3
########################
# RPi Weather Station
# Adam Hedley
# March 2018
#
# Read Data from Teensy
# Data is captured every 1 second
# Dust Sensor
# Gas sensors
########################

#import Teensy_Serial_Check
import serial
import time
import datetime
import RPi.GPIO as GPIO
import mysql.connector
from mysql.connector import errorcode

print (" ")
print ("Wait a bit before kicking off...")
print (" ")

i = 2
loops = 0
while i > loops:

  print("Hold up mofo...",i,"seconds")
  print(" ")
  time.sleep(1)
  i -= 1

print(" ")
print("Teensy Reset pin set-up...")
print(" ")
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

RST_pin = 7
GPIO.setup(RST_pin, GPIO.OUT)

# Not going to use reset
#print("Teensy reset in progress...")
#print(" ")
#GPIO.output(RST_pin,0)
#print("Reset Enabled")
#print(" ")
#time.sleep(2)
#GPIO.output(RST_pin,1)
#print("Reset HIGH")
#print(" ")

# "ls /dev/tty" in terminal to find device on USB port
# ls /dev/serial/by-id or by-path
# http://www.roman10.net/2011/06/23/serial-port-communication-in-python/#comment-1877


# Splits data out read back from Teensy board separated by ' - '
def split_data(sens_pos, serial_data):
  data_split = serial_data.decode().split(' - ')
  sensor = data_split[sens_pos]
  #print ("Split Data   ", sensor) # For checking
  #print(" ")
  return sensor


# Read Data off Serial Port from Teensy
def read_data():

  print ("*** Setting up Serial Bus ***")
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

  print("Serial Bus Selected:  ",ser)
  print(" ")

  print("Read Data")
  print(" ")
  ser = serial.Serial('/dev/serial/by-id/usb-Teensyduino_USB_Serial_2908420-if00',9600, timeout=1)
  read_serial = ser.readline()
  print("Data Read From Serial Bus:",read_serial) # For checking
  print(" ")

  # Teensy is a bit temperamental and connection randomly stops working. Running Teensy_Serial_Chech.py seems to fix the issue.
  # Running it within this file doesn't seem to work, so call Teensy_Serial_Chech.py instead
  
  # If nothing is read back on read_serial
  if not read_serial:
    exec (open ("./Teensy_Serial_Check.py").read())
    read_serial = ser.readline()
    print ("Teensy Check Read Serial ",read_serial)

  # Read PM sensor
  PM_OUT = split_data(0, read_serial)
  PM_OUT = float(PM_OUT)

  # Read Gas Sensor
  CO = split_data(1, read_serial)
  CO = float(CO)
  NOx = split_data(2, read_serial)
  NOx = float(NOx)

  # Read Battery Voltage
  batt = split_data(3, read_serial)
  batt = float(batt)

  print("Data Cell Split:")
  print(" PM2.5 ",PM_OUT," CO ppm ",CO," NOx ppb ",NOx," Battery Voltage ", batt)
  print(" ")

  # Close serial port
  ser.close()
  return PM_OUT, CO, NOx, batt

# Save Data to file
def save_data(location, data1, data2):
  # Open log file
  f = open(location, 'a+')

  # Get date and time, set format
  now = datetime.datetime.now()
  timestamp = now.strftime("%d.%m.%Y %H:%M")

  # Set values to put in log file

  # Piece together data to put on single line of log file
  logdata = str(timestamp) + " " + str(data1) + str(data2) + " \n"
  # Write to log file
  print ("Printing RAW Logdata  ", logdata) # For checking
  print (" ")
  f.write(logdata)
  f.close()

# Save Data to mysql database
def database(PM25, CO, NOx, sec, timestamp):
  print("Ready to end data to table Teensy Raw")
  try:
    # Open a connection to the MySQL Server
    cnx = mysql.connector.connect(user='<enter user>', password='<enter password>', database='<enter database for sensors>')
    # Create a new Cursor
    cursor = cnx.cursor()
    # Insert a new row into the table
    add_data = ("INSERT INTO Teensy_Raw "
               "(PM25, CO, NOx, datetime, date) "
               "VALUES (%s, %s, %s, %s, %s)")

    # Setting the data values
    data_val = (PM25, CO, NOx, sec, timestamp)
    print("data_val: ",data_val)
    print(" ")
    # Passing all the data to the cursor
    cursor.execute(add_data, data_val)
    # Make sure the data is committed to the database
    cnx.commit()
    # Close the cursor
    cursor.close()

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database doesn not exist")
    else:
      print(err)
  else:
    cnx.close()

  print("MySQL connection is closed")
  print(" ")


def main():

  print(" ")
  print("Capturing Teensy Data....")
  print(" ")

  # Reads serial data and splits it
  (PM_OUT, CO, NOx, batt) = read_data()

  # Readable TimeStamp
  now = datetime.datetime.now()
  timestamp = now.strftime("%d.%m.%Y %H:%M")

  # TimeStamp for HighCharts
  secs = float(time.time())
  secs = secs*1000

  database(PM_OUT, CO, NOx, secs, timestamp)

  # Battery voltage to web page
  now = datetime.datetime.now()
  timestamp = now.strftime("%d.%m.%Y %H:%M")

  print ("Ready to send data into table battvoltage ")
  print (" ")

  try:
    # Open a connection to the MySQL Server
    cnx = mysql.connector.connect(user='<enter user>', password='<enter password>', database='<enter database for sensors>')
    # Create a new Cursor
    cursor = cnx.cursor()
    # Timestamp for HighCharts
    secs = float(time.time())
    secs = secs*1000

    print("Voltage: ", batt)
    print(" ")
    # Insert a new row into the table
    add_data = ("INSERT INTO battvoltage "
               "(datetime, voltage, date) "
               "VALUES (%s, %s, %s)")

    # Setting the data values
    data_val = (secs, batt, timestamp)
    print("data_val: ",data_val)
    print(" ")
    # Passing all the data to the cursor
    cursor.execute(add_data, data_val)
    # Make sure the data is committed to the database
    cnx.commit()
    # Close the cursor
    cursor.close()

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      print("Database does not exist")
    else:
      print(err)
  else:
    cnx.close()

  print("MySQL connection is closed")
  print(" ")

  exit()

if __name__=="__main__":
		main()
