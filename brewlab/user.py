import serial
import os
import datetime
from time import sleep
import pandas as pd
import numpy as np

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
    print("\nPlease input an integer for temperature from 4 - 23 C")
    while (True):    
        reply = int(input())
        if (reply >= 4 and reply <= 23):
            print("\nSetting fermenter temperature to "+ str(reply)+" C\n")
            return float(reply)
        else:
            print("error type an integer between 4 and 23\n")

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

    today = datetime.date.today()
    filename = "data/" + str(today)+ "_data.csv"

    return df, filename

def setup_ferms(ser1, ser2, ser3):
    if fermChoose(1, ser1):
        fTemp1 = fermTemp(1)
    else:
        fTemp1 = np.NaN

    if fermChoose(2, ser2):
        fTemp2 = fermTemp(2)
    else:
        fTemp2 = np.NaN

    if fermChoose(3, ser3):
        fTemp3 = fermTemp(3)
    else:
        fTemp3 = np.NaN

    return (fTemp1, fTemp2, fTemp3)
