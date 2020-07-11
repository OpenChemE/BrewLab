import serial
from time import sleep
import os
import sys

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

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