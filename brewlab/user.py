import serial
import os
import datetime
from time import sleep
import pandas as pd
import numpy as np

from openpyxl import Workbook

print(os.environ.get("MODE") == "dev")

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

# FUNCTIONS
# This function asks user if they will be using a fermenter for the experiment
def fermChoose(fermNum,ser):
    ferm_stat = False   
    print("Will fermenter " + str(fermNum) + " be run for the experiment? type y/n for yes or no")  # Ask user which fermenters will be run
    while (True):
        reply = str(input())
        if (reply == "y" or reply == "Y"):
            ferm_stat = True
            print("Activating fermenter " + str(fermNum))
            ser.write('1') #send message to Arduino to log data from fermenter        
            sleep(0.1)
            return ferm_stat
        elif (reply == "n" or reply == "N"):
            # Send message to Arduino to NOT log data from fermenter
            ser.write('0') # Send message to Arduino to log data from fermenter        
            sleep(0.1)
            return ferm_stat
        else:
            "error type y for yes or n for no\n"

# This function asks user what temperature they want to set fermenter to
def fermTemp(fermNum):
    print("\nplease input an integer for temperature from 4 - 23 C")
    while (True):    
        reply = int(input())
        if (reply >= 4 and reply <= 23):
            print("\nSetting fermenter temperature to "+ str(reply)+" C\n")
            return float(reply)
        else:
            print("error type an integer between 4 and 23\n")

# This function generates a filename based on the date & test number
# It checks existing files in the folder to ensure that no overwrite occurs            
def createDataFile(wb):
    path = os.chdir("data")  # Define directory
    today = datetime.date.today()  # Get current date

    testNum = 1  # Set current test number
    dest_filename = str(today)+ "test" + str(testNum) +".xlsx"  # Generate file name

    fileList = os.listdir(path)  # Get list of items in folder

    lengthList = len(fileList)  # Get list length

    for x in range(0,lengthList):  # For the length of the list
        fileName = fileList[x]  # Get the name of the list

        if str(fileName[0:10]) == str(today):  # If date of file is today
            testNum = testNum + 1  # Increase test number by 1

    dest_filename = str(today)+ "test" + str(testNum) +".xlsx"  # Create name  
    wb.save(filename = dest_filename)  # Save workbook
    return dest_filename

def init_df():
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

    return df
