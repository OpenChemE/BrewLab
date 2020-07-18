import serial
from time import sleep
import os
import sys
from collections import namedtuple
from numpy import NaN

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

Fermenter = namedtuple(
    'Fermenter',
    [
        'active',
        'auto',
        'temp',
        'serialCon'
    ]
)

# Begin communication with arduinos connected to the system
COM1 = 'COM3'
COM2 = 'COM4'
COM3 = 'COM5'

# Connects to Arduino and prints hello to confirm connection
def ardCon(COM_NUM):
    print ("Connecting to Arduino\n")
    try:
        ser = serial.Serial(COM_NUM, 9600, timeout=0) # Establish the connection on specified COM port
        sleep(2)
        ser.write("Hello")
        sleep(5)
        reply = ser.readline()
        print(reply.strip('\n'))
    except AttributeError as e:

        print(e)
        print ("No connection to Arduino, terminating program")
        sys.exit()
    return ser


def setup():
    ferm1 = Fermenter(
        active=False,
        auto=True,
        temp=NaN,
        serialCon=ardCon(COM1)
    )

    ferm2 = Fermenter(
        active=False,
        auto=True,
        temp=NaN,
        serialCon=ardCon(COM2)
    )

    ferm3 = Fermenter(
        active=False,
        auto=True,
        temp=NaN,
        serialCon=ardCon(COM3)
    )

    return [ferm1, ferm2, ferm3]


def get_data(fermenter, serialCon):

    # Define flags
    PHflag = False
    DOflag = False
    tflag = False
    Tflag = False

    serialCon.write('F')  # Let arduino know to send fermenter data
    sleep(0.5)
    data = serialCon.readline()  # Readline from buffer and remove newline

    if (str(data[0:2]) == fermenter):
        sleep(0.1)
        count = 0  # Reset counter for data collection
        while (count < 4):  # While all data has not been collected
            data = serialCon.readline()  # Readline from buffer and remove newline

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
                except:
                    ph_1 = len(PH1) - 1

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
