import serial
from time import sleep
import os
import sys
import pandas as pd
from collections import namedtuple
from numpy import NaN
from kivy.logger import Logger

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

Fermenter = namedtuple(
    'Fermenter',
    [
        'id',       # The ID of the fermenter ie: F1
        'name',     # The full name of the fermenter
        'active',   # True when data is being collected
        'auto',     # True unless manual control is enabled
        'temp',     # Float value of temperature setpoint
        'serialCon' # Arduino Serial Connection
    ]
)

# Begin communication with arduinos connected to the system
COM1 = 'COM3'
COM2 = 'COM4'
COM3 = 'COM5'

def ardCon(COM_NUM):
    """
    Connects to Arduino and prints hello to confirm connection
    """
    Logger.info("App: Connecting to Arduino")
    try:
        ser = serial.Serial(COM_NUM, 9600, timeout=0) # Establish the connection on specified COM port
        sleep(2)
        ser.write("Hello".encode())
        sleep(5)

        reply = ser.readline().decode()
        Logger.info("App: Connection established")
    except AttributeError as e:
        Logger.warning("App: Got AttributeError: {}".format(e))
        Logger.critical("App: No connection to Arduino, terminating program")
        sys.exit()
    return ser

def setup():
    """
    Connect to arduinos and return list of fermenter objects
    """
    ferm1 = Fermenter(
        id='F1',
        name='Fermenter 1',
        active=False,
        auto=True,
        temp=NaN,
        serialCon=ardCon(COM1)
    )

    ferm2 = Fermenter(
        id='F2',
        name='Fermenter 2',
        active=False,
        auto=True,
        temp=NaN,
        serialCon=ardCon(COM2)
    )

    ferm3 = Fermenter(
        id='F3',
        name='Fermenter 3',
        active=False,
        auto=True,
        temp=NaN,
        serialCon=ardCon(COM3)
    )

    return [ferm1, ferm2, ferm3]

def activateArd(fermenter):
    """
    Activates Arduino during setup
    """
    if fermenter.active is True:
        fermenter.serialCon.write('1'.encode())
        sleep(0.1)
    else:
        fermenter.serialCon.write('0'.encode())
        sleep(0.1)

def get_data(fermenter, serialCon):
    """
    Retrieves and parses data from Arduino.

    Logic adapted from CHBREWERY V4.py written by Thanos Kritharis
    """

    # Define flags
    PHflag = False
    DOflag = False
    tflag = False
    Tflag = False

    # Let arduino know to send fermenter data
    serialCon.write('F'.encode())
    sleep(0.5)
    data = serialCon.readline().decode().strip('\n')  # Readline from buffer and remove newline

    if (str(data[0:2]) == fermenter):
        sleep(0.1)
        count = 0  # Reset counter for data collection
        while (count < 4):  # While all data has not been collected
            data = serialCon.readline().decode().strip('\n')  # Readline from buffer and remove newline

            if (str(data[0:2]) =="ti" and tflag == False):
                time_1 = float(data[2:])
                count += 1
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
                except Exception as e:
                    Logger.warning("App: Caught exception: {}".format(e))
                    ph_1 = NaN

                count += 1
                PHflag = True
            
            if (str(data[0:2]) == "DO" and DOflag == False):
                try:
                    do_1 = float(data[2:])
                except:
                    do_1 = 0
                count += 1
                DOflag = True
            
            if (str(data[0:2]) == "Te" and Tflag == False):
                T1 = float(data[2:])
                count += 1
                Tflag = True

            if tflag and Tflag and DOflag and PHflag:
                row = [time_1, ph_1, do_1, T1]
                return row
