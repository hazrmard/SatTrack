#!/usr/bin/env python

# use stuct.pack to convert >255 ints to bytes to write
# then use bit shifting to restore them to int

################################################
# Module:   servo.py
# Created:  2 April 2008
# Author:   Brian D. Wendt
#   http://principialabs.com/
# Version:  0.3
# License:  GPLv3
#   http://www.fsf.org/licensing/
'''
Provides a serial connection abstraction layer
for use with Arduino "MultipleSerialServoControl" sketch.
'''
################################################

import serial
import struct

# Assign Arduino's serial port address
#   Windows example
#     usbport = 'COM3'
#   Linux example
#     usbport = '/dev/ttyUSB0'
#   MacOSX example
#     usbport = '/dev/tty.usbserial-FTALLOK2'
usbport = 'COM3'

# Set up serial baud rate
ser = serial.Serial(usbport, 9600, timeout=1)

# How to run:
# from pythonServoController import *
# >> move(motor #, angle)

def move(servo, angle):
    '''Moves the specified servo to the supplied angle.

    Arguments:
        servo
          the servo number to command, an integer from 1-4
        angle
          the desired servo angle, an integer from 0 to 180

    (e.g.) >>> servo.move(2, 90)
           ... # "move servo #2 to 90 degrees"'''

    if (0 <= angle <= 359):
        ser.write(chr(255))
        ser.write(chr(servo))
        ser.write(chr(struct.pack('>h',angle)[0]))
        ser.write(chr(struct.pack('>h',angle)[1]))
    else:
        raise ValueError('Servo must be between 1 and 6 and angle must be between 0 and 359 deg.')
