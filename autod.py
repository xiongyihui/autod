#!/usr/bin/env python

import os
import subprocess
from time import sleep
from pyudev import Context, Monitor, MonitorObserver

PWD = os.path.dirname(os.path.realpath(__file__))
LPC11U35_DOWNLOAD_TOOL = os.path.join(PWD, 'LinuxNXPISP.sh')
LPC11U35_DOWNLOAD_FILE = 'stream.bin'
MBED_INTERFACE_TOOL = os.path.join(PWD, 'flash_binary.py')

def lpc11u35_event(action):
    if action == 'add':
        print('lpc11u35 is found')
        subprocess.call([LPC11U35_DOWNLOAD_TOOL, LPC11U35_DOWNLOAD_FILE])
    elif action == 'remove':
        print('lpc11u35 is removed')
        
def mbed_interface_event(action):
    if action == 'add':
        print('mbed interface is found')
        subprocess.call(MBED_INTERFACE_TOOL)
    elif action == 'remove':
        print('mbed interface is removed')

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
        sleep(1)
        
except:
    print('exit')
    observer.stop()
