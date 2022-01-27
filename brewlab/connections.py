import serial
from time import sleep
import os
import re
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
    ]
)

# Begin communication with Arduino
COM1 = 'COM3'

def ardCon(COM_NUM='COM4'):
    """
    Connects to Arduino and prints hello to confirm connection
    """
    Logger.info("App: Connecting to Arduino")
    try:
        ser = serial.Serial(COM_NUM, 9600, timeout=30) # Establish the connection on specified COM port
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
    )

    ferm2 = Fermenter(
        id='F2',
        name='Fermenter 2',
        active=False,
        auto=True,
        temp=NaN,
    )

    ferm3 = Fermenter(
        id='F3',
        name='Fermenter 3',
        active=False,
        auto=True,
        temp=NaN,
    )

    return [ferm1, ferm2, ferm3]

def activateArd(serialCon, fermenter):
    """
    Activates Arduino during setup
    """
    if fermenter.active is True:
        serialCon.write('1'.encode())
        sleep(0.1)
    else:
        serialCon.write('0'.encode())
        sleep(0.1)

def get_data(serialCon):
    """
    Retrieves and parses data from Arduino.
    """

    values = []

    # Let arduino know to send fermenter data
    while len(values) < 3:
        serialCon.write('F'.encode())
        sleep(10)

        data = serialCon.readline().decode()
        values = [float(s) for s in re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", data)]

    return values
