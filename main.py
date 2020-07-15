# Import libraries
from time import sleep
import time
import serial
from openpyxl import Workbook
import pandas as pd
import numpy as np

import os
import datetime
import matplotlib.pyplot as plt
import keyboard # Using module keyboard
import sys

from brewlab.connections import ardCon
from brewlab.user import fermChoose, fermTemp, createDataFile

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

arrays = [
    np.array([
        'Fermenter 1', 'Fermenter 1', 'Fermenter 1', 'Fermenter 1',
        'Fermenter 2', 'Fermenter 2', 'Fermenter 2', 'Fermenter 2',
        'Fermenter 3', 'Fermenter 3', 'Fermenter 3', 'Fermenter 3',
    ]),
    np.array([
        'Time (min)', 'Temp (C)', 'pH', 'DO (mg/L)',
        'Time (min)', 'Temp (C)', 'pH', 'DO (mg/L)',
        'Time (min)', 'Temp (C)', 'pH', 'DO (mg/L)',
    ]),
]

df = pd.DataFrame(columns=arrays)

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

    if (ferm1 == True):
        ser1.write('F')  # let arduino know to send F1 data
        time.sleep(0.5)
        data = ser1.readline()  # readline from buffer and remove newline
        auto = True

        if (str(data[0:2]) == "F1"):
            time.sleep(0.1)
            count = 0  # reate counter for data collection
            while (count < 4):  # while all data has not been collected
                data = ser1.readline()  # readline from buffer and remove newline

                if (str(data[0:2]) =="ti" and tflag == False):
                    time_1 = float(data[2:])
                    count = count + 1
                    tflag = True
            
                if (str(data[0:2]) == "PH" and PHflag == False):
                    try:
                        strCount = 0
                        for x in range (0,len(data)):
                            check = data[x]
                            if (check == "."):
                                strCount = strCount + 1
                                strPlace = x
                        if (strCount > 1):
                            ph_1 = float(data[(x-1):].strip('\r'))
                        else:
                            ph_1 = float(data[2:].strip('\r'))
                    except:
                        ph_1 = len(PH1) - 1

                    count = count + 1
                    PHflag = True
                
                if (str(data[0:2]) == "DO" and DOflag == False):
                    try:
                        do_1 = float(data[2:])
                    except:
                        do_1 = 0
                    count = count + 1
                    DOflag = True
                
                if (str(data[0:2]) == "Te" and Tflag == False):
                    T1 = float(data[2:])
                    count = count + 1
                    Tflag = True

                if tflag and Tflag and DOflag and PHflag:
                    row = [time_1, ph_1, do_1, T1]
                    print(row)
                
            # Reset Flags
            PHflag = False
            DOflag = False
            tflag = False
            Tflag = False
            
            i1 = i1 + 1
            saveCount = saveCount + 1
            if (saveCount == 10):
                wb.save(filename = fileName)
                saveCount = 0

    if i1 > 1 and auto is True:
        if fTemp1 < T1:
            ser1.write('PT')
        else:
            ser1.write('PF')
    
    sleep(60)
       
    print ("next iteration")
