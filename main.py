# Import libraries
from time import sleep
import time
import serial
import pandas as pd
import numpy as np

import os
import datetime
import matplotlib.pyplot as plt
import keyboard # Using module keyboard
import sys

from brewlab.connections import ardCon, get_data
from brewlab.user import fermChoose, fermTemp, init_df
from brewlab.control import fermControl

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

# Begin communication with arduinos connected to the system
COM1 = 'COM3'
COM2 = 'COM4'
COM3 = 'COM5'

ser1 = ardCon(COM1)
ser2 = ardCon(COM2)
ser3 = ardCon(COM3)

# Ask users which fermenters they want to use
ferm1 = fermChoose(1,ser1)
if (ferm1 == True):
    fTemp1 = fermTemp(1)
ferm2 = fermChoose(2,ser2)
if (ferm2 == True):
    fTemp2 = fermTemp(2)
ferm3 = fermChoose(3,ser3)
if (ferm3 == True):
    fTemp3 = fermTemp(3)

df = init_df()

sleep(1)  # Wait a bit for arduino to catch up

# Define flags
PHflag = False
DOflag = False
tflag = False
Tflag = False

i1 = 0

saveCount = 0  # Counter for saving excel sheet
dataRun = False

while True:

    row = get_data('F1', ser1)
    fermControl(ser1, fTemp1, row[3], True)
    
    sleep(60)
       
    print ("next iteration")
