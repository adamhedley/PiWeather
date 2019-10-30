#!/usr/bin/python3
########################
# RPi Weather Station
# Adam Hedley
# February 2018
########################

import time
import datetime
import smbus
import mysql.connector
from mysql.connector import errorcode

DEVICE1 = 0x76 # BMP280 device I2C address (Temperature and Pressure)
DEVICE2 = 0x40 # Si7021 device I2C address (Temperature and Humidity)

bus = smbus.SMBus(1)


def read_word_data_unsigned(addr, reg):
  results = bus.read_word_data(addr, reg)
  return results


def read_word_data_signed(addr, reg):
  results = bus.read_word_data(addr, reg)
  if results > 32767:
    results -= 65536
  return results

def read_byte_data(addr, reg):
  results = bus.read_byte_data(addr, reg)
  return results

def read_byte(addr):
  results = bus.read_byte(addr)
  return results

def write_byte_data(addr, reg, value):
  bus.write_byte_data(addr, reg, value)

def write_byte(addr, value):
  bus.write_byte(addr, value)

def rd_BMP280ID(addr=DEVICE1):
  # Chip ID Register Address
  REG_ID     = 0xD0
  (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
  return (chip_id, chip_version)


def BMP280(addr=DEVICE1):
  # power mode
  # POWER_MODE=0 # sleep mode
  POWER_MODE=1 # forced mode
  # POWER_MODE=2 # forced mode
  #POWER_MODE=3 # normal mode

  # temperature resolution
  # OSRS_T = 0 # skipped
  OSRS_T = 1 # 16 Bit
  # OSRS_T = 2 # 17 Bit
  # OSRS_T = 3 # 18 Bit
  # OSRS_T = 4 # 19 Bit
  # OSRS_T = 5 # 20 Bit

  # pressure resolution
  # OSRS_P = 0 # pressure measurement skipped
  OSRS_P = 1 # 16 Bit ultra low power
  # OSRS_P = 2 # 17 Bit low power
  # OSRS_P = 3 # 18 Bit standard resolution
  # OSRS_P = 4 # 19 Bit high resolution
  # OSRS_P = 5 # 20 Bit ultra high resolution

  # filter settings
  # FILTER = 0 #
  # FILTER = 1 #
  # FILTER = 2 #
  # FILTER = 3 #
  FILTER = 4 #
  # FILTER = 5 #
  # FILTER = 6 #
  # FILTER = 7 #

  # standby settings
  # T_SB = 0 # 000 0,5ms
  # T_SB = 1 # 001 62.5 ms
  # T_SB = 2 # 010 125 ms
  # T_SB = 3 # 011 250ms
  T_SB = 4 # 100 500ms
  # T_SB = 5 # 101 1000ms
  # T_SB = 6 # 110 2000ms
  # T_SB = 7 # 111 4000ms

  CONFIG = (T_SB <<5) + (FILTER <<2) # combine bits for config
  CTRL_MEAS = (OSRS_T <<5) + (OSRS_P <<2) + POWER_MODE # combine bits for ctrl_meas

  # print ("CONFIG:",CONFIG)
  # print ("CTRL_MEAS:",CTRL_MEAS)

  # Register Data
  BMP280_REGISTER_DIG_T1 = 0x88
  BMP280_REGISTER_DIG_T2 = 0x8A
  BMP280_REGISTER_DIG_T3 = 0x8C
  BMP280_REGISTER_DIG_P1 = 0x8E
  BMP280_REGISTER_DIG_P2 = 0x90
  BMP280_REGISTER_DIG_P3 = 0x92
  BMP280_REGISTER_DIG_P4 = 0x94
  BMP280_REGISTER_DIG_P5 = 0x96
  BMP280_REGISTER_DIG_P6 = 0x98
  BMP280_REGISTER_DIG_P7 = 0x9A
  BMP280_REGISTER_DIG_P8 = 0x9C
  BMP280_REGISTER_DIG_P9 = 0x9E
  BMP280_REGISTER_CHIPID = 0xD0
  BMP280_REGISTER_VERSION = 0xD1
  BMP280_REGISTER_SOFTRESET = 0xE0
  BMP280_REGISTER_CONTROL = 0xF4
  BMP280_REGISTER_CONFIG  = 0xF5
  BMP280_REGISTER_STATUS = 0xF3
  BMP280_REGISTER_TEMPDATA_MSB = 0xFA
  BMP280_REGISTER_TEMPDATA_LSB = 0xFB
  BMP280_REGISTER_TEMPDATA_XLSB = 0xFC
  BMP280_REGISTER_PRESSDATA_MSB = 0xF7
  BMP280_REGISTER_PRESSDATA_LSB = 0xF8
  BMP280_REGISTER_PRESSDATA_XLSB = 0xF9

  dig_T1 = 0.0
  dig_T2 = 0.0
  dig_T3 = 0.0
  dig_P1 = 0.0
  dig_P2 = 0.0
  dig_P3 = 0.0
  dig_P4 = 0.0
  dig_P5 = 0.0
  dig_P6 = 0.0
  dig_P7 = 0.0
  dig_P8 = 0.0
  dig_P9 = 0.0

  # Read Calibration
  # Reset
  write_byte_data(addr, BMP280_REGISTER_SOFTRESET, 0xB6)
  time.sleep(0.2)
  write_byte_data(addr, BMP280_REGISTER_CONTROL, CTRL_MEAS)
  time.sleep(0.2)
  write_byte_data(addr, BMP280_REGISTER_CONFIG, CONFIG)
  time.sleep(0.2)

  dig_T1 = read_word_data_unsigned(addr, BMP280_REGISTER_DIG_T1)
  dig_T2 = read_word_data_signed(addr, BMP280_REGISTER_DIG_T2)
  dig_T3 = read_word_data_signed(addr, BMP280_REGISTER_DIG_T3)

  dig_P1 = read_word_data_unsigned(addr, BMP280_REGISTER_DIG_P1)
  dig_P2 = read_word_data_signed(addr, BMP280_REGISTER_DIG_P2)
  dig_P3 = read_word_data_signed(addr, BMP280_REGISTER_DIG_P3)
  dig_P4 = read_word_data_signed(addr, BMP280_REGISTER_DIG_P4)
  dig_P5 = read_word_data_signed(addr, BMP280_REGISTER_DIG_P5)
  dig_P6 = read_word_data_signed(addr, BMP280_REGISTER_DIG_P6)
  dig_P7 = read_word_data_signed(addr, BMP280_REGISTER_DIG_P7)
  dig_P8 = read_word_data_signed(addr, BMP280_REGISTER_DIG_P8)
  dig_P9 = read_word_data_signed(addr, BMP280_REGISTER_DIG_P9)

  # Measure RAW data
  raw_temp_msb = read_byte_data(addr, BMP280_REGISTER_TEMPDATA_MSB) # read raw temperature msb
  raw_temp_lsb = read_byte_data(addr, BMP280_REGISTER_TEMPDATA_LSB) # read raw temperature lsb
  raw_temp_xlsb = read_byte_data(addr, BMP280_REGISTER_TEMPDATA_XLSB) # read raw temperature xlsb
  raw_press_msb = read_byte_data(addr, BMP280_REGISTER_PRESSDATA_MSB) # read raw pressure msb
  raw_press_lsb = read_byte_data(addr, BMP280_REGISTER_PRESSDATA_LSB) # read raw pressure lsb
  raw_press_xlsb = read_byte_data(addr, BMP280_REGISTER_PRESSDATA_XLSB) # read raw pressure xlsb

  raw_temp = (raw_temp_msb <<12) + (raw_temp_lsb <<4) + (raw_temp_xlsb >>4) # combine 3 bytes  msb 12 bits left, lsb 4 bits left, xlsb 4 bits right
  raw_press = (raw_press_msb <<12) + (raw_press_lsb <<4) + (raw_press_xlsb >>4) # combine 3 bytes  msb 12 bits left, lsb 4 bits left, xlsb 4 bits right

  # formula for temperature from datasheet
  var1 = (raw_temp / 16384.0 - dig_T1 / 1024.0) * dig_T2
  var2 = (raw_temp / 131072.0 - dig_T1 / 8192.0) * (raw_temp / 131072.0 - dig_T1 / 8192.0) * dig_T3
  temp = (var1 + var2) / 5120.0

  t_fine = (var1 + var2) # Used for pressure calculation

  # formula for pressure from datasheet
  var1 = t_fine / 2.0-64000.0
  var2 = var1 * var1 * dig_P6 / 32768.0
  var2 = var2 + var1 * dig_P5 * 2
  var2 = var2 / 4.0 + dig_P4 * 65536.0
  var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
  var1 = (1.0 + var1 / 32768.0) * dig_P1
  press = 1048576.0 - raw_press
  press = (press - (var2 / 4096.0)) * 6250.0 / var1
  var1 = dig_P9 * press * press / 2147483648.0
  var2 = press * dig_P8 / 32768.0
  press = press + (var1 + var2 + dig_P7) / 16.0

  # Calculating Altitude
  P0 = 1013.25
  P1 = press
  T = temp
  # Hypsometric formula
  altit = ((((P0 / P1)**(1/5.257)) - 1) * (T + 273.15)) / 0.0065

  # Where
  # P0 = Pressure at sea level in Pa = 101,325 Pa
  # P1 = Pressure measured from sensor
  # T = measured temperature in degrees C from sensor
  # altitude ~60m
  return temp, press, altit

def Si7021(addr = DEVICE2):

  MEAS_RELATIVE_HUM_HOLD_MSTR_MODE = 0XE5
  MEAS_RELATIVE_HUM_NO_HOLD_MSTR_MODE = 0XF5
  MEAS_TEMPERATURE_HOLD_MSTR_MODE = 0XE3
  MEAS_TEMPERATURE_NO_HOLD_MSTR_MODE = 0XF3
  RD_TEMP_PREVIOUS_RH_MEAS = 0XE0
  RESET = 0XFE
  WR_RHT_USR_REG1 = 0XE6
  RD_RHT_USR_REG1 = 0XE7
  WR_HEATER_CTRL_REG = 0X51
  RD_HEATER_CTRL_REG = 0X11
##  RD_ELEC_ID_BYTE1 = 0XFA 0X0F
##  RD_ELEC_ID_BYTE2 = 0XFC 0XC9
##  RD_FW_VER = 0X84 0XB8

  write_byte(addr, MEAS_RELATIVE_HUM_NO_HOLD_MSTR_MODE)

  time.sleep(0.3)

  # Read 2 bytes, Humidit
  data0 = read_byte(addr)
  data1 = read_byte(addr)

  # Convert the data
  humidity = ((data0 * 256 + data1) * 125 / 65536.0) - 6

  time.sleep(0.3)

  write_byte(addr, MEAS_TEMPERATURE_NO_HOLD_MSTR_MODE)

  time.sleep(0.3)

  #Read data 2 bytes, Temperature
  data0 = read_byte(addr)
  data1 = read_byte(addr)

  # Convert the data and output it
  celsTemp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
  fahrTemp = celsTemp * 1.8 + 32

  return celsTemp, fahrTemp, humidity


def main():

  # For CRON: 5 min run intervals use
  # */5 * * * * GY21P_Sensors_CRON.py

  # Initial Read of Devices
  (chip_id, chip_version) = rd_BMP280ID()
  print ("BMP280 Chip ")
  print ("Chip ID       :", chip_id)
  print ("Version       :", chip_version)
  print ("")

  (temp, press, altit) = BMP280()
  print ("Temperature   :  %.2f C" %temp)
  print ("Pressure      :  %.2f Pa" %press)
  print ("Altitude      :  %.2f m" %altit)
  print ("")

  (celsTemp, fahrTemp, humidity) = Si7021()
  print ("Si7021 Chip")
  print ("Relative Humidity is         : %.2f %%" %humidity)
  print ("Temperature in Celsius is    : %.2f C" %celsTemp)
  print ("Temperature in Fahrenheit is : %.2f F" %fahrTemp)
  print ("")

  # Set measured data to 2 dp
  B_temp = "%.2f" %temp
  B_press = "%.2f" %press
  B_altit = "%.2f" %altit

  S_celsTemp = "%.2f" %celsTemp
  S_humidity = "%.2f" %humidity

  print ("Ready to send data into table ")
  print (" ")

  # Get date and time, set format
  now = datetime.datetime.now()
  timestamp = now.strftime("%d.%m.%Y %H:%M")

  # Timestamp for HighCharts
  secs = float(time.time())
  secs = secs*1000

  try:
    # Open a connection to the MySQL Server
    cnx = mysql.connector.connect(user='<enter user>', password='<enter password>', database='<enter database for sensors>')
    # Create a new Cursor
    cursor = cnx.cursor()

    # Insert a new row into the table BMP280
    add_data = ("INSERT INTO BMP280 "
               "(temperature, pressure, altitude, datetime, date) "
               "VALUES (%s, %s, %s, %s, %s)")

    # Setting the data values
    data_val = (B_temp, B_press, B_altit, secs, timestamp)
    print("data_val: ",data_val)
    print(" ")
    # Passing all the data to the cursor
    cursor.execute(add_data, data_val)
    # Make sure the data is committed to the database
    cnx.commit()

    # Insert a new row into the table Si7021
    add_data = ("INSERT INTO Si7021 "
               "(temperature, humidity, datetime, date) "
               "VALUES (%s, %s, %s, %s)")

    # Setting the data values
    data_val = (S_celsTemp, S_humidity, secs, timestamp)
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

  exit()

if __name__=="__main__":
		main()
