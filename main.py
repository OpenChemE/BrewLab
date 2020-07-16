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
from brewlab.user import fermChoose, fermTemp, init_df, setup_ferms
from brewlab.control import fermControl

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

# Begin communication with arduinos connected to the system
COM1 = 'COM3'
COM2 = 'COM4'
COM3 = 'COM5'

def run():
    ser1 = ardCon(COM1)
    ser2 = ardCon(COM2)
    ser3 = ardCon(COM3)

    # Ask users which fermenters they want to use
    (temp1, temp2, temp3) = setup_ferms(ser1, ser2, ser3)

    df = init_df()

    sleep(1)  # Wait a bit for arduino to catch up

    # Begin loop to read data
    while True:

        try:
            row = get_data('F1', ser1)
            fermControl(ser1, temp1, row[3], True)
        except Exception as e:
            print("Could not get data on Fermenter 1. Caught exception: ", e)

        sleep(60)

        print ("next iteration")

if __name__ == "__main__":
    run()
