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

# Create workbook
wb = Workbook()  # generate workbook
ws1 = wb.active  # activate workbook
ws1.title = "Fermentation Data"

fileName = createDataFile(wb)
print(str(fileName) + " data file generated")
    
# Create lists to hold data
if (ferm1 == True):
    T1 = list()
    PH1 = list()
    DO1 = list()
    t1 = list()
    ws1['A1'] = "Fermenter 1 Data"
    # define data entry headers
    ws1['A2'] = "Time (min)"
    ws1['B2'] = "Temperature (C)"
    ws1['C2'] = "PH"
    ws1['D2'] = "Dissolved Oxygen (mg/L)"
    
if (ferm2 == True):
    T2 = list()
    PH2 = list()
    DO2 = list()
    t2 = list()
    ws1['E1'] = "Fermenter 2 Data"
    # define data entry headers
    ws1['E2'] = "Time (min)"
    ws1['F2'] = "Temperature (C)"
    ws1['G2'] = "PH"
    ws1['H2'] = "Dissolved Oxygen (mg/L)"
    
if (ferm3 == True):
    T3 = list()
    PH3 = list()
    DO3 = list()
    t3 =list()
    ws1['I1'] = "Fermenter 3 Data"
    # define data entry headers
    ws1['I2'] = "Time (min)"
    ws1['J2'] = "Temperature (C)"
    ws1['K2'] = "PH"
    ws1['L2'] = "Dissolved Oxygen (mg/L)"

# Use infinite loop for data acquisition
fermAct = True
sleep(0.5)  # Wait a bit for arduino to catch up

# Define flags
PHflag = False
DOflag = False
tflag = False
Tflag = False
figure1Active = False
figure2Active = False
figure3Active = False
count1 = 0
count2 = 0
count3 = 0
i1 = 0  # Counter for excel sheet
i2 = 0
i3 = 0
saveCount = 0  # Counter for saving excel sheet
dataRun = False

while (fermAct == True):

    if (ferm1 == True):
        ser1.write('F')  # let arduino know to send F1 data
        time.sleep(0.5)
        data = ser1.readline()  # readline from buffer and remove newline
        print(data)
        if (str(data[0:2]) == "F1"):
            time.sleep(0.1)
            count = 0  # reate counter for data collection
            while (count < 4):  # while all data has not been collected
                data = ser1.readline()  # readline from buffer and remove newline
                print(data)
            
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
                        DO1.append(float(data[2:]))
                    except:
                        DO1.append(0)
                    count = count + 1
                    DOflag = True
                
                if (str(data[0:2]) == "Te" and Tflag == False):
                    T1.append(float(data[2:]))
                    count = count + 1
                    Tflag = True

                row = []
                
            #Reset Flags
            PHflag = False
            DOflag = False
            tflag = False
            Tflag = False
            
            #Record Data into Excel file
            d = ws1.cell(row = 2+i1, column = 1)#call cell
            d.value = t1[i1] #set cell value
            d = ws1.cell(row = 2+i1, column = 2)#call cell
            d.value = T1[i1] #set cell value
            d = ws1.cell(row = 2+i1, column = 3)#call cell
            d.value = PH1[i1] #set cell value
            d = ws1.cell(row = 2+i1, column = 4)#call cell
            d.value = DO1[i1] #set cell value
            i1 = i1 + 1
            saveCount = saveCount + 1
            if (saveCount == 10):
                wb.save(filename = fileName)
                saveCount = 0

            count1 += 1  # Increase index
    if (i1 > 1):
        if (fTemp1 < T1[(i1-1)]):
            ser1.write(('PT\n'))
        else:
            ser1.write(('PF\n'))
    
    start_time = time.time()
    elapsed_time = 0
    while(elapsed_time < 5):
        elapsed_time = time.time() - start_time
        # Wait 1 minute before next iteration
       
    print ("next iteration")