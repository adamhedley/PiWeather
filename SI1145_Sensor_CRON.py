#!/usr/bin/python3
##########################
# RPi Weather Station
# Adam Hedley
# July 2018
#
# Si1145 UV Sensor
# Capture LUX and UV Index
###########################

import time
import datetime
import smbus
import RPi.GPIO as GPIO
import mysql.connector
from mysql.connector import errorcode

# Just so all the reads dont use 100% of cpu....?
time.sleep(5)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Set DIO out to drive LED's for UV Index
# for future 
UV1_LED = 22  # 1-2 Low
UV2_LED = 12  # 3-5 Moderate
UV3_LED = 13  # 6-7 High
UV4_LED = 15  # 8-10 Very High
UV5_LED = 16  # 11 Extreme

GPIO.setup(UV1_LED, GPIO.OUT)
GPIO.setup(UV2_LED, GPIO.OUT)
GPIO.setup(UV3_LED, GPIO.OUT)
GPIO.setup(UV4_LED, GPIO.OUT)
GPIO.setup(UV5_LED, GPIO.OUT)

# I2C Address
SI1145_IC2_ADDR = 0x60

bus = smbus.SMBus(1)

def read_word_data_unsigned(addr, reg):
  results = bus.read_word_data(addr, reg)
  return results

def read_byte_data(addr, reg):
  results = bus.read_byte_data(addr, reg)
  return results

def write_byte_data(addr, reg, value):
  bus.write_byte_data(addr, reg, value)

def write_byte(addr, value):
  bus.write_byte(addr, value)

# Write Parameter
# Put PARAM data into PARAM_WR
# Write data in PARAM_WR to Parameter
# For every Write to COMMAND clear RESPONSE REGISTER and confrim
def write_param(addr, p, v):
  write_byte_data(addr, COMMAND, NOP)
  resp = read_byte_data(addr, RESPONSE)
  print ("Response Should be Zero  ", resp)
  write_byte_data(addr, PARAM_WR, v)
  write_byte_data(addr, COMMAND, p | PARAM_SET)
  value = read_byte_data(addr, PARAM_RD)
  resp = read_byte_data(addr, RESPONSE)
  print ("Response Should be non zero  ", resp)
  return value, resp

# Read unsigned 16-bit value
def read_word_u16(addr, reg, little_endian=True):
  result = read_word_data_unsigned(addr,reg) & 0xFFFF
  if not little_endian:
    result = ((result << 8) & 0xFF00) + (result >> 8)
  return result

#def read_device(addr, reg):
#  return read_ic(addr,reg, little_endian=True)


# REGISTERS
PART_ID                          = 0x00
REV_ID                           = 0x01
SEQ_ID                           = 0x02
INT_CFG                          = 0x03
IRQ_EN                           = 0x04
IRQ_MODE1                        = 0x06
IRQ_MODE2                        = 0x06
HW_KEY                           = 0x07
MEAS_RATE0                       = 0x08
MEAS_RATE1                       = 0x09
PS_LED21                         = 0x0F
PS_LED3                          = 0x10
UCOEF0                           = 0x13
UCOEF1                           = 0x14
UCOEF2                           = 0x15
UCOEF3                           = 0x16
PARAM_WR                         = 0x17
COMMAND                          = 0x18
RESPONSE                         = 0x20
IRQ_STAT                         = 0x21
ALS_VIS_DATA0                    = 0x22
ALS_VIS_DATA1                    = 0x23
ALS_IR_DATA0                     = 0x24
ALS_IR_DATA1                     = 0x25
PS1_DATA0                        = 0x26
PS1_DATA1                        = 0x27
PS2_DATA0                        = 0x28
PS2_DATA1                        = 0x29
PS3_DATA0                        = 0x2A
PS3_DATA1                        = 0x2B
UV_INDEX0                        = 0x2C
UV_INDEX1                        = 0x2D
PARAM_RD                         = 0x2E
CHIP_STAT                        = 0x30


# COMMANDS
PARAM_QUERY                      = 0x80
PARAM_SET                        = 0xA0
NOP                              = 0x0
RESET                            = 0x01
BUSADDR                          = 0x02
PS_FORCE                         = 0x05
GET_CAL                          = 0x12
ALS_FORCE                        = 0x06
PSALS_FORCE                      = 0x07
PS_PAUSE                         = 0x09
ALS_PAUSE                        = 0x0A
PSALS_PAUSE                      = 0xB
PS_AUTO                          = 0x0D
ALS_AUTO                         = 0x0E
PSALS_AUTO                       = 0x0F


# PARAMETERS
I2C_ADDR                         = 0x00
CHLIST                           = 0x01
PSLED12_SEL                      = 0x02
PSLED3_SEL                       = 0x03
PS_ENCODE                        = 0x05
ALS_ENCODE                       = 0x06
PS1_ADCMUX                       = 0x07
PS2_ADCMUX                       = 0x08
PS3_ADCMUX                       = 0x09
PS_ADC_COUNTER                   = 0x0A
PS_ADC_GAIN                      = 0x0B
PS_ADC_MISC                      = 0x0C
ALS_IR_ADCMUX                    = 0x0E
AUX_ADCMUX                       = 0x0F
ALS_VIS_ADC_COUNTER              = 0x10
ALS_VIS_ADC_GAIN                 = 0x11
ALS_VIS_ADC_MISC                 = 0x12
LED_REC                          = 0x1C   # Reserved
ALS_IR_ADC_COUNTER               = 0x1D
ALS_IR_ADC_GAIN                  = 0x1E
ALS_IR_ADC_MISC                  = 0x1F

# Read Response Register
def response(addr = SI1145_IC2_ADDR):
    res_reg = read_byte_data(addr, RESPONSE)
    #print (" ")
    #print ("Response Register = ", res_reg)
    #print (" ")

    # Check Error and clear Response register if error occures
    if res_reg <= 15:
        error = "NO ERROR"
    elif res_reg == 128:
        error = "INVALID SETTING"
        write_byte_data(addr, COMMAND, NOP)
    elif res_reg == 136:
        error = "PS1 ADC OVERFLOW"
        write_byte_data(addr, COMMAND, NOP)
    elif res_reg == 137:
        error = "PS2 ADC OVERFLOW"
        write_byte_data(addr, COMMAND, NOP)
    elif res_reg == 138:
        error = "PS3 ADC OVERFLOW"
        write_byte_data(addr, COMMAND, NOP)
    elif res_reg == 140:
        error = "ALS VIS ADC OVERFLOW"
        write_byte_data(addr, COMMAND, NOP)
    elif res_reg == 141:
        error = "ALS IR ADC OVERFLOW"
        write_byte_data(addr, COMMAND, NOP)
    elif res_reg == 142:
        error = "AUX ADC OVERFLOW"
        write_byte_data(addr, COMMAND, NOP)

    # Only Print Error Status if there is an Error
    if res_reg >= 20:
      print ("Error Status    ", error)
      print (" ")

    return res_reg, error


# Reset Device
def reset(addr = SI1145_IC2_ADDR):
  write_byte_data(addr, MEAS_RATE0, 0x00)
  write_byte_data(addr, MEAS_RATE1, 0x00)
  write_byte_data(addr, IRQ_EN, 0x00)
  write_byte_data(addr, IRQ_MODE1, 0x00)
  write_byte_data(addr, IRQ_MODE2, 0x00)
  write_byte_data(addr, INT_CFG, 0x00)
  write_byte_data(addr, IRQ_STAT, 0xFF)
  write_byte_data(addr, COMMAND, RESET)
  time.sleep(0.05)
  write_byte_data(addr,HW_KEY, 0x17)
  time.sleep(0.05)



# Set up
def setup(addr = SI1145_IC2_ADDR):

  # Enable UV Index Measurement Coefficients
  write_byte_data(addr, UCOEF0, 0x7B) #0x29) not sure where these values come from
  write_byte_data(addr, UCOEF1, 0x6B) #0x89) set to original values as per data sheet
  write_byte_data(addr, UCOEF2, 0x01) #0x02)
  write_byte_data(addr, UCOEF3, 0x00)

  # Enable / disable UV sensors
  # CHLIST DATA - Set bits accordingly (7:0). Page 47 of Data Sheet
  EN_UV			= 1		# Enable UV Index
  EN_AUX		= 1		# Enable Auxiliary Channel
  EN_ALS_IR		= 1		# Enable Ambient Light Sensor IR Channel
  EN_ALS_VIS	= 1		# Enable Ambient Light Sensor Visible Channel
  # RESERVED 			# BIT 3 is Reserved
  EN_PS3		= 0		# Enable Proximity Sensor Channel 3
  EN_PS2		= 0		# Enable Proximity Sensor Channel 2
  EN_PS1		= 0		# Enable Proximity Sensor Channel 1

  CHLIST_DATA	= (EN_UV <<7) + (EN_AUX <<6) + (EN_ALS_IR <<5) + (EN_ALS_VIS <<4) + (EN_PS3 <<2) + (EN_PS2 <<1) + (EN_PS1)

  write_param(addr, CHLIST, CHLIST_DATA)

  #########################################################################
  # AUX_DATA / UVINDEX is set for UV
  # Temperature or Vdd Reading

  #AUX_ADC	= 0x65	# Temperature Sensor (Relative temperature, not absolute)
  #AUX_ADC	= 0x75	# Vdd Voltage

  #write_param(addr, AUX_ADCMUX, AUX_ADC)

  #########################################################################
  # Enable / disable interrupts
  INT_OE	= 0x00		# INT pin is never driven
  #INT_OE	= 0x01		# int pin driven low whenever an IRQ_STATUS and corresponding IRQ_ENABLE bits match

  PS3_IE	= 0		# 0 = Never Assert / 1 = Assert INT pin when PS3_INT is set by the internal sequencer
  PS2_IE	= 0		# 0 = Never Assert / 1 = Assert INT pin when PS3_INT is set by the internal sequencer
  PS1_IE	= 0		# 0 = Never Assert / 1 = Assert INT pin when PS3_INT is set by the internal sequencer
  ALS_IE	= 0		# 0 = Never Assert / 1 = Assert INT pin when PS3_INT is set by the internal sequencer

  IRQ_ENABLE = (PS3_IE <<4) + (PS2_IE <<3) + (PS1_IE <<2) + ALS_IE

  write_byte_data(addr, INT_CFG, INT_OE)
  write_byte_data(addr, IRQ_EN, IRQ_ENABLE)

  #########################################################################
  # External LED's (Proximity Sensors) - Currently none used

  # Program LED Current
  # PS_LED3(3:0) = LED3
  # PS_LED12(7:4) = LED2
  # PS_LED12(3:0) = LED1

  #                  Typ mA
  # PS_LEDn = 0001    5.6
  # PS_LEDn = 0010    11.2
  # PS_LEDn = 0011    22.4
  # PS_LEDn = 0100    45
  # PS_LEDn = 0101    67
  # PS_LEDn = 0110    90
  # PS_LEDn = 0111    112
  # PS_LEDn = 1000    135
  # PS_LEDn = 1001    157
  # PS_LEDn = 1010    180
  # PS_LEDn = 1011    202
  # PS_LEDn = 1100    224
  # PS_LEDn = 1101    269
  # PS_LEDn = 1110    314
  # PS_LEDn = 1111    359

  #PS_ILED1 = 0000
  #PS_ILED2 = 0000
  #PS_ILED3 = 0000

  #PS_ILED21 = (PS_ILED2 <<4) + (PS_ILED1)

  #PS1_DIODE = 0x03 # Large IR Photodiode
  #PS1_DIODE = 0x00 # Small IR Photodiode

  #PS2_DIODE = 0x03 # Large IR Photodiode
  #PS2_DIODE = 0x00 # Small IR Photodiode

  #PS3_DIODE = 0x03 # Large IR Photodiode
  #PS3_DIODE = 0x00 # Small IR Photodiode

  #PS1_LED = 000	# No LED Drive
  #PS1_LED = xx1	# LED1 Drive Enabled
  #PS2_LED = 000	# No LED Drive
  #PS2_LED = xx1	# LED2 Drive Enabled
  #PS3_LED = 000	# No LED Drive
  #PS3_LED = xx1	# LED3 Drive Enabled

  #PSLED12_SELECT = (PS2_LED <<4) + (PS1_LED)
  #PSLED3_SELECT = PS3_LED

  # PS_ADC_GAIN increases irLED pulse width and ADC integration time by a factor of
  # ( 2 ^ PS_ADC_GAIN) for all PS measurements
  #ADC_CLK = 0x0	# ADC clock is divided by 1 - Fastest clocks
  #ADC_CLK = 0x4	# ADC clock is divided by 16
  #ADC_CLK = 0x5	# ADC clock is divided by 32


  # PS_ADC_COUNTER is the recovery period the ADC takes before making a PS measurement

  #PS_SDC_REC = 000	# 1 ADC Clock (50 ns times 2^PS_ADC_GAIN)
  #PS_SDC_REC = 001	# 7 ADC Clock (350 ns times 2^PS_ADC_GAIN)
  #PS_SDC_REC = 010	# 15 ADC Clock (750 ns times 2^PS_ADC_GAIN)
  #PS_SDC_REC = 011	# 31 ADC Clock (1.55 μs times 2^PS_ADC_GAIN)
  #PS_SDC_REC = 100	# 63 ADC Clock (3.15 μs times 2^PS_ADC_GAIN)
  #PS_SDC_REC = 101	# 127 ADC Clock (6.35 μs times 2^PS_ADC_GAIN)
  #PS_SDC_REC = 110	# 255 ADC Clock (12.75 μs times 2^PS_ADC_GAIN)
  #PS_SDC_REC = 111	# 511 ADC Clock (25.55 μs times 2^PS_ADC_GAIN)

  #PS_ADC_COUNT = (PS_SDC_REC <<4) + (0000)


# PS_ADC_MISC setting ADC sensitivity and mode

  #PS_RANGE = 0	# Normal Signal Range
  #PS_RANGE = 1	# High Signal Range (Gain divided 14.5) - useful in operation under direct sunlight

  #PS_ADC_MODE = 0	# Raw ADC Measurement Mode
  #PS_ADC_MODE = 1	# Normal Proximity Measurement Mode

  #PS_ADC_OTHER = (PS_RANGE <<5) + (PS_ADC_MODE <<2)

  #write_byte_data(addr, PS_LED21, PS_ILED21)    	# Program LED current
  #write_param(addr, PS1_ADCMUX, PS1_DIODE)  		# Set Photodiode Size
  #write_param(addr, PSLED12_SEL, PSLED12_SELECT)	# Drive / No Drive LEDs 1 and or 2)
  #write_param(addr, PS_ADC_GAIN, ADC_CLK)			# Increase PS ADC clock width
  #write_param(addr, PS_ADC_COUNTER, PS_ADC_COUNT)	# 511 clock cycles to next PS measurement
  #write_param(addr, PS_ADC_MISC, PS_ADC_OTHER) 	# PS ADC in High range and normal mode


  #########################################################################
  # Ambient Light Sensor (ALS) Set up, Infra-red and Visible

  # Infra-red Set-up


  # ALS_IR_ADCMUX is for setting IR Photodiode size
  ALS_IR_SIZE = 0x00	# Small IR Photodiode - Default
  #ALS_IR_SIZE = 0x03	# Large IR Photodiode

  # ALS_IR_ADC_GAIN increases the ADC integration time for IR Ambient measurements by a factor of (2 ^ ALS_IR_ADC_GAIN) Max gain is 128 (0x7)
  ALS_IR_GAIN = 0x0		# ADC Clock is divided by 1
  #ALS_IR_GAIN = 0x4		# ADC Clock is divided by 16
  #ALS_IR_GAIN = 0x6		# ADC Clock is divided by 64

  # ALS_IR_ADC_COUNTER is the recovery period the ADC takes before making an ALS-IR measurement
  #IR_ADC_REC = 0x00 #000	# 1 ADC clock (50 ns times 2^ALS_IR_ADC_GAIN)
  #IR_ADC_REC = 0x10 #001	# 7 ADC Clock (350 ns times 2^ALS_IR_ADC_GAIN)
  #IR_ADC_REC = 0x20 #010	# 15 ADC Clock (750 ns times 2^ALS_IR_ADC_GAIN)
  #IR_ADC_REC = 0x30 #011	# 31 ADC Clock (1.55 μs times 2^ALS_IR_ADC_GAIN)
  #IR_ADC_REC = 0x40 #100	# 63 ADC Clock (3.15 μs times 2^ALS_IR_ADC_GAIN)
  #IR_ADC_REC = 0x50 #101	# 127 ADC Clock (6.35 μs times 2^ALS_IR_ADC_GAIN)
  #IR_ADC_REC = 0x60 #110	# 255 ADC Clock (12.75 μs times 2^ALS_IR_ADC_GAIN)
  IR_ADC_REC = 0x70 #111	# 511 ADC Clock (25.55 μs times 2^ALS_IR_ADC_GAIN)

  # ALS_IR_ADC_MISC sets high sensitivity or high signal range. High signal range is useful in operation under direct sunlight
  #IR_RANGE = 0x00	# Normal Signal Range
  IR_RANGE = 0x20	# High Signal Range (Gain divided by 14.5)

  # Visible Set-up

  # ALS_VIS_ADC_GAIN increases the ADC integration time for Visible measurements by a factor of (2 ^ ALS_VIS_ADC_GAIN) Max gain is 128 (0x7)
  ALS_VIS_GAIN = 0x0		# ADC Clock is divided by 1
  #ALS_VIS_GAIN = 0x4		# ADC Clock is divided by 16
  #ALS_VIS_GAIN = 0x6		# ADC Clock is divided by 64

  # ALS_VIS_ADC_COUNTER is the recovery period the ADC takes before making an ALS-VIS measurement
  #VIS_ADC_REC = 0x00	#000: 1 ADC Clock (50 ns times 2^ALS_VIS_ADC_GAIN)
  #VIS_ADC_REC = 0x10	#001: 7 ADC Clock (350 ns times 2^ALS_VIS_ADC_GAIN)
  #VIS_ADC_REC = 0x20	#010: 15 ADC Clock (750 ns times 2^ALS_VIS_ADC_GAIN)
  #VIS_ADC_REC = 0x30	#011: 31 ADC Clock (1.55 μs times 2^ALS_VIS_ADC_GAIN)
  #VIS_ADC_REC = 0x40	#100: 63 ADC Clock (3.15 μs times 2^ALS_VIS_ADC_GAIN)
  #VIS_ADC_REC = 0x50	#101: 127 ADC Clock (6.35 μs times 2^ALS_VIS_ADC_GAIN)
  #VIS_ADC_REC = 0x60	#110: 255 ADC Clock (12.75 μs times 2^ALS_VIS_ADC_GAIN)
  VIS_ADC_REC = 0x70	#111: 511 ADC Clock (25.55 μs times 2^ALS_VIS_ADC_GAIN)

  # ALS_VIS_ADC_MISC sets high sensitivity or high signal range. High signal range is useful in operation under direct sunlight
  #VIS_RANGE = 0x00	# Normal Signal Range
  VIS_RANGE = 0x20	# High Signal Range (Gain divided by 14.5)


  ALS_IR_ALIGN	= 0		# When set, ADC reports 16 LSB of 17-bit ADC
  ALS_VIS_ALIGN	= 0		# When set, ADC reports 16 LSB of 17-bit ADC

  ALS_ENCODING = (ALS_IR_ALIGN <<5) + (ALS_VIS_ALIGN <<4)


  write_param(addr, ALS_IR_ADCMUX, ALS_IR_SIZE)
  write_param(addr, ALS_IR_ADC_GAIN, ALS_IR_GAIN)
  write_param(addr, ALS_IR_ADC_COUNTER, IR_ADC_REC)
  write_param(addr, ALS_IR_ADC_MISC, IR_RANGE)
  write_param(addr, ALS_VIS_ADC_GAIN, ALS_VIS_GAIN)
  write_param(addr, ALS_VIS_ADC_COUNTER, VIS_ADC_REC)
  write_param(addr, ALS_VIS_ADC_MISC, VIS_RANGE)

  write_param(addr, ALS_ENCODE, ALS_ENCODING)

  #########################################################################
  # Run Mode

  # MEASE_RATE = (MEAS_RATE1[15:8])(MEAS_RATE0[7:0])
  # Set to zero for Forced Measurement Mode.
  # Else 16 bit value multiplied by 31.25 us represents time duration between wake-up periods where measurements are made
  # Read measurements at least twice this to ensure new set is captured
  # FFFF = 65535 = ~ 2 seconds
  # 0F00 = 3840 = 1.2 seconds

  MEAS_R0 = 0xFF
  MEAS_R1 = 0xFF

  write_byte_data(addr, MEAS_RATE0, MEAS_R0)
  write_byte_data(addr, MEAS_RATE1, MEAS_R1)

  write_byte_data(addr, COMMAND, PSALS_AUTO)	# Set device to Auto Run


def read_uv(addr=0x60):

  vis = read_word_u16(addr, ALS_VIS_DATA0)
  ir = read_word_u16(addr, ALS_IR_DATA0)
  uv = read_word_u16(addr, UV_INDEX0)
  uv_index = uv/100
  return vis, ir, uv, uv_index



def main():

  # For CRON: 5 min run intervals use
  # */5 * * * * SI1145_Sensor_CRON.py

  # Reset Device on start up
  print ("Si1145 Reset in progress")
  reset()

  # Run Set-up on start up
  print ("Si1145 Set-up in progress")
  setup()

  # Response Register
  response()
  res_reg = read_byte_data(0x60, RESPONSE)
  print ("Response Register   ", res_reg)

  time.sleep(1)

  print (" ")
  print ("Capturing Si1145 Sensor Data...")

  # Read device and get data
  (vis, ir, uv, uv_index) = read_uv()

  # Read the response register for errors
  (res_reg, error) = response()

  # Irr W/m
  irr = round(ir*0.0079,2)

  # calibration - subract value when sensor is covered for zero value
  vis = vis - 259
  ir = ir - 251

  # Set measured data to 2 dp
  vis = "%.2f" %vis
  ir = "%.2f" %ir
  uv = "%.2f" %uv

  # Device doesnt always read back, so check and read again if error
  if (vis == -259.00 and ir == -251.00):
    print ("Resetting device...")
    reset()
    print ("Set-up in progress")
    setup()
    response()
    res_reg = read_byte_data(0x60, RESPONSE)
    print ("Response Register    ", res_reg)
    time.sleep(1)
    (vis, ir, uv, uv_index) = read_uv()
    # Re-Read the response register for errors
    (res_reg, error) = response()
    # Irr W/m
    irr = round(ir*0.0079,2)
    # calibration - subract value when sensor is covered for zero value
    vis = vis - 259
    ir = ir - 251
    # Set measured data to 2 dp
    ir = "%.2f" %ir
    uv = "%.2f" %uv


  # Setting LEDs for UIV Index Display

  if uv_index >= 11:
      index = "Extreme"
      LED_OUT = "101111"  # Set as a sting in order to use slicing
  elif uv_index >= 8:
      index = "Very High"
      LED_OUT = "100111"
  elif uv_index >= 6:
      index = "High"
      LED_OUT = "100011"
  elif uv_index >= 3:
      index = "Moderate"
  elif uv_index < 3:
      index = "Low"
      LED_OUT = "100001"

  # Slicing to get specific bit and convert to int
  LED1 = int(LED_OUT[0])
  LED2 = int(LED_OUT[1])
  LED3 = int(LED_OUT[2])
  LED4 = int(LED_OUT[3])
  LED5 = int(LED_OUT[4])

  # For debug
  print ("LED1  ", LED1)
  print ("LED2  ", LED2)
  print ("LED3  ", LED3)
  print ("LED4  ", LED4)
  print ("LED5  ", LED5)
  print (" ")

  # Set LED output
  GPIO.output(UV1_LED, LED1)
  GPIO.output(UV2_LED, LED2)
  GPIO.output(UV3_LED, LED3)
  GPIO.output(UV4_LED, LED4)
  GPIO.output(UV5_LED, LED5)


  # For debug and confirmation
  print ("UV :       ", uv, "Lux")
  print ("UV Index:  ", uv_index, "index") # index was not in " " 17/06/2019
  print ("Vis :      ", vis, "Lux")
  print ("IR  :      ", ir, "Lux")
  print ("Irr W/m :  ", irr)
  print ("  ")

  # Timestamp for HighCharts
  secs = float(time.time())
  secs = secs*1000

  # Get date and time, set format
  now = datetime.datetime.now()
  timestamp = now.strftime("%d.%m.%Y %H:%M")

  print ("Ready to send data into table ")
  print (" ")

  try:
    # Open a connection to the MySQL Server
    cnx = mysql.connector.connect(user='<enter user>', password='<enter password>', database='<enter database for sensors>')
    # Create a new Cursor
    cursor = cnx.cursor()

    # Insert a new row into the table
    add_data = ("INSERT INTO Si1145 "
               "(UV, xindex, UV_Index, VIS, IR, datetime, date) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s)")

    # Setting the data values
    data_val = (uv, index, uv_index, vis, ir, secs, timestamp)
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

  # Set values to put in log file
  if res_reg >= 20:
    SI_sen = "UV " + str(uv) + " UV Index " + str(uv_index) + " " + str(index) + " Vis " + str(vis) + " IR " + str(ir) + " Error: " + str(error)
  elif res_reg <= 15:
    SI_sen = "UV " + str(uv) + " UV Index " + str(uv_index) + " " + str(index) + " Vis " + str(vis) + " IR " + str(ir)

  # Piece together data to put on single line of log file
  logdata = str(timestamp) + " " + SI_sen + "\n"

  # Write to log file
  print (logdata) # For checking

  exit()

if __name__=="__main__":
		main()
