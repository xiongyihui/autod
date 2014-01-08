#!/usr/bin/env python

import sys, os
from time import sleep
import pyOCD
from pyOCD.board import MbedBoard

PWD = os.path.dirname(os.path.realpath(__file__))
binary_file = os.path.join(PWD, 'arch_pro_test_v1.1.bin')

board = None

try:

    board = MbedBoard.chooseBoard()
    flash = board.flash
    target= board.target
    
    target.halt()

    flash.flashBinary(binary_file)
    
    target.reset()
        
finally:
    if board != None:
        board.uninit()
        
