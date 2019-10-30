#!/usr/bin/python3
########################
# RPi Weather Station
# Adam Hedley
# September 2018
#
# Shut down the RPi when
# batteries are low via
# Adafruit Trinket
# Random shut downs. Easy write to same file at start to monitor shut down and restarts
########################

import RPi.GPIO as GPIO
import time
import datetime
import os
import mysql.connector
from mysql.connector import errorcode

# Output to Teensy to signal Pi is on/off
pi_act = 23

# Input from Trinket on Pin xx
shtdn = 18

# GPIO pin numbering mode
GPIO.setmode(GPIO.BOARD)
# Ignore warnings
GPIO.setwarnings(False)
# Setup GPIO pin 23 as output and add pull-up
GPIO.setup(pi_act, GPIO.OUT)
# Setup GPIO pin 18 as input and add pull-down
GPIO.setup(shtdn, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
# Setup rising edge event detection
GPIO.add_event_detect(shtdn, GPIO.RISING)

# Drive output to Teensy so it knows if its powered up or not
GPIO.output(pi_act, 1)
print(" ")
print("RPi Active set HIGH")

def read_word_data_unsigned(addr, reg):
  results = bus.read_word_data(addr, reg)
  return results

# Save Data to mysql database
def database(state, timestamp):
  try:
    # Open a connection to the MySQL Server
    cnx = mysql.connector.connect(user='<enter user>', password='<enter password>', database='<enter database for sensors>')
    # Create a new Cursor
    cursor = cnx.cursor()
    # Insert a new row into the table
    add_data = ("INSERT INTO Shutdown "
               "(PWR_SHT, date) "
               "VALUES (%s, %s)")

    # Setting the data values
    data_val = (state, timestamp)
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


def main():

  print (" ")
  print ("Shut Down Script Active....")
  time.sleep(10)

  now = datetime.datetime.now()
  timestamp = now.strftime("%d/%m/%Y %H:%M")

  print("Ready to write to database")
  print(" ")
  database('POWER UP', timestamp)
  print("Power Up written to database")
  print(" ")

  while True:

    print("Listening for shutdown signal from Teensy")
    print(" ")
    # Run loop every 2 seconds. Free running causes 100% cpu usage
    time.sleep(2)

    # when edge is detected, wait 5 seconds and confirm shut down is still high - removes glitches
    if GPIO.event_detected(shtdn):
      time.sleep(5)
      state = GPIO.input(shtdn)
      print("state", state)

      if (state == 1):
        print("Shut Down Active")
        print(" ")

        now = datetime.datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M")

        print(" ")
        print("Low Battery. Shutting Down...")

        database('Shut Down', timestamp)

        time.sleep(3)
        print ("Bye bye sweet pea")
        os.system("sudo shutdown -h now")


if __name__=="__main__":
		main()
