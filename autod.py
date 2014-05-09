#!/usr/bin/env python

import os
import subprocess
from time import sleep
from pyudev import Context, Monitor, MonitorObserver
import RPi.GPIO as GPIO

PWD = os.path.dirname(os.path.realpath(__file__))
LPC11U35_DOWNLOAD_TOOL = os.path.join(PWD, 'LinuxNXPISP.sh')
LPC11U35_DOWNLOAD_FILE = 'stream.bin'
MBED_INTERFACE_TOOL = os.path.join(PWD, 'flash_binary.py')


LED_IO = [7, 8, 11, 12, 15, 16]
RED_LED = 8
BLUE_LED = 12
GREEN_LED = 16

GPIO.setmode(GPIO.BOARD)
for i in LED_IO:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)    

red_led = None
blue_led = None    

def lpc11u35_event(action):
    if action == 'add':
        print('lpc11u35 is found')
        blue_led = GPIO.PWM(BLUE_LED, 10)
        blue_led.start(50)
        subprocess.call([LPC11U35_DOWNLOAD_TOOL, LPC11U35_DOWNLOAD_FILE])
        blue_led.changeDutyCycle(100)
    elif action == 'remove':
        print('lpc11u35 is removed')
        blue_led.changeDutyCycle(0)
        
def mbed_interface_event(action):
    if action == 'add':
        print('mbed interface is found')
        red_led = GPIO.PWM(RED_LED, 10)
        red_led.start(50)
        subprocess.call(MBED_INTERFACE_TOOL)
    elif action == 'remove':
        print('mbed interface is removed')
        red_led.changeDutyCycle(0)

def device_event(action, device):

    if device.device_type == 'disk':
        if device.get('ID_VENDOR_ID') == '1fc9':
            lpc11u35_event(action)
        elif device.get('ID_VENDOR_ID') == '0d28':
            mbed_interface_event(action)
        
            
        
print('Auto download deamon')

context = Context()
monitor = Monitor.from_netlink(context)
monitor.filter_by(subsystem='block')
observer = MonitorObserver(monitor, device_event)

print('Start to detect usb mass storage')
observer.start()

try:
    while True:
        GPIO.ouput(GREEN_LED, GPIO.HIGH)
        sleep(1)
        GPIO.ouput(GREEN_LED, GPIO.LOW)
        sleep(1)
        
except:
    print('exit')
    GPIO.cleanup()
    observer.stop()
    
