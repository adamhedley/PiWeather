#!/usr/bin/python3
#########################
# RPi Weather Station
# Adam Hedley
# March 2018
#
# Measure Wind Speed
########################

import RPi.GPIO as GPIO
import time
import math
import datetime
import mysql.connector
from mysql.connector import errorcode

# Anemometer connected from Pin 11 to GND
fan_pin = 11

# Set to zero
counter = 0
count = 0
turn_s = 0
data_add = 0

# GPIO pin numbering mode
GPIO.setmode(GPIO.BOARD)
# Ignore warnings
GPIO.setwarnings(False)
# Setup GPIO pin as input and add pulldown
GPIO.setup(fan_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# Setup falling edge event detection
GPIO.add_event_detect(fan_pin, GPIO.FALLING)

print ("Capturing Wind Speed Data...")

while True:

  # Free running causes 100 cpu usage need to calculate second pause or sort this out or move to teensy
  time.sleep(1)

  # Set while loop to run for 2 seconds
  t_end = time.time() + 2

  # Capture pulses for 2 seconds for more accurate slow speeds
  # Amenometer pulses twice per revolution
  # Divide by 4 for number of turns per second

  while time.time() < t_end:

    # Free running uses 100% CPU
    # Set sample rate: for max speed of 67 m/s (150 mph)
    # 118 turns per 2 seconds = 1 turn per 0.017 seconds
    # Sample every 17 ms
    time.sleep(0.017)

    # when falling edge is detected
    if GPIO.event_detected(fan_pin):
      counter = counter + 1
      turn_s = counter / 4
      print("Number of turns... ", turn_s) # For checking
      print(" ")

  # Angular velocity, w (rad/s) to linear velocity, v (m/s)

  # 1 turn = 2 * pi radians
  # v = wr

  # radius of wind meter (m)
  r = 0.09

  # Angular velocity
  w  = turn_s * 2 * math.pi

  # wind speed m/s
  v = w * r

  # Wind speed mph
  # 1 m/s = 2.23694 mph
  mph = v * 2.23694

  print("Wind Speed %.2f" %v, "m/s   %.2f" %mph, "mph" )  # For checking

  # Reset counters / timers
  t_end = 0
  counter = 0
  turn_s = 0

  # Counter to log average wind speed over x time
  count = count + 1
  #print ("Count  ",count) # For checking

  # Reading sensor for 2 seconds
  # Average count loop needs to 30 times
  # for a minutes average. Multiplied by
  # avg_time to get average wind speed.
  # Set avg_time in minutes
  avg_time = 2
  time_period = (30 * avg_time)

  if count < time_period:
    data_add = data_add + v
    #print ("Data_add", data_add)


  if count >= time_period:
    #print ("time_period  ", time_period)
    #print (" ")
    count = 0
    data_avg = data_add / time_period
    mph = data_avg * 2.23694
    data_avg = "%.2f" %data_avg
    mph = "%.2f" %mph
    print ("Data Average   ", data_avg)

    # Get data and time, set format
    now = datetime.datetime.now()
    timestamp = now.strftime("%d.%m.%Y %H:%M")

    # Timestamp for HighCharts
    secs = float(time.time())
    secs = secs*1000

    print ("Ready to send data into table ")
    print (" ")

    try:
      # Open a connection to the MySQL Server
      cnx = mysql.connector.connect(user='<enter user>', password='<enter password>', database='<enter database for sensors>')
      # Create a new Cursor
      cursor = cnx.cursor()

      # Insert a new row into the table
      add_data = ("INSERT INTO Wind "
                 "(avg_ms, avg_mph, datetime, date) "
                 "VALUES (%s, %s, %s, %s)")

      # Setting the data values
      data_val = (data_avg, mph, secs, timestamp)
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
        print("Database does not exist")
      else:
        print(err)
    else:
      cnx.close()

    print("MySQL connection is closed")
    print(" ")

    # Reset average data variables
    data_add = 0
    data_avg = 0
    mph = 0

if __name__=="__main__":
		main()
