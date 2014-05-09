#!/usr/bin/env python

import os
import subprocess
import RPi.GPIO as GPIO
from time import sleep
from pyudev import Context, Monitor, MonitorObserver

PWD = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_TOOL = os.path.join(PWD, 'LinuxNXPISP.sh')
DOWNLOAD_FILE = 'test.bin'
LED_IO = [11, 12, 15, 16]
BLUE_LED = 12
GREEN_LED = 16

GPIO.setmode(GPIO.BOARD)
for i in LED_IO:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, GPIO.HIGH)

def device_event(action, device):

    if device.device_type == 'disk' and device.get('ID_VENDOR_ID') == '1fc9':
        if action == 'add':
            print('get a device')
            subprocess.call([DOWNLOAD_TOOL, DOWNLOAD_FILE])
            GPIO.output(BLUE_LED, GPIO.HIGH)
        elif action == 'remove':
            print('device is removed')
            GPIO.output(BLUE_LED, GPIO.LOW)
        
print('Auto download deamon')

context = Context()
monitor = Monitor.from_netlink(context)
monitor.filter_by(subsystem='block')
observer = MonitorObserver(monitor, device_event)

print('Start to detect usb mass storage')
observer.start()

try:
    while True:
        GPIO.output(GREEN_LED, GPIO.HIGH)
        sleep(1)
        GPIO.output(GREEN_LED, GPIO.LOW)
        sleep(1)
        
except Exception as e:
    print(e)
    print('exit')
    GPIO.cleanup()
    observer.stop()
