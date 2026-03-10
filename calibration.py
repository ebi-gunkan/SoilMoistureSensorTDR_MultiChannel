# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time

SELECTOR_C = 14		#bit2
SELECTOR_B = 15		#bit1
SELECTOR_A = 18		#bit0

def Initialize_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SELECTOR_C,GPIO.OUT)
    GPIO.setup(SELECTOR_B,GPIO.OUT)
    GPIO.setup(SELECTOR_A,GPIO.OUT)

    GPIO.output(SELECTOR_C,0)
    GPIO.output(SELECTOR_B,0)
    GPIO.output(SELECTOR_A,0)

def Control_ChSelector(ch):
    GPIO.output(SELECTOR_C,(ch >> 2) & 0x01)
    GPIO.output(SELECTOR_B,(ch >> 1) & 0x01)
    GPIO.output(SELECTOR_A,ch & 0x01)

if __name__ == '__main__':
    try:
        Initialize_GPIO()
        Control_ChSelector(0)
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()
