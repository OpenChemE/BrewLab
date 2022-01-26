import serial
import os
import datetime
from time import sleep
import pandas as pd
import numpy as np

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

MULTI_COLUMN_LAYOUT = [
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

def init_df():
    """
    Initializes dataframe and gives app the filename
    """
    df = pd.DataFrame(columns=MULTI_COLUMN_LAYOUT)

    today = datetime.date.today()
    path = "data/" + str(today)+ "/"

    if not os.path.exists(path):
        os.makedirs(path)

    num = len(os.listdir(path)) + 1
    filename = "data/" + str(today)+ "/" + "run_{}".format(num) + "_data.csv"

    df.to_csv(filename)

    return df, filename


def resample_data(filename, timeframe):
    """
    Reads data from the CSV and formats it to the users request. 
    """

    # Read data from generated csv
    try:
        df = pd.read_csv(filename, index_col=0,
                         header=[0, 1], parse_dates=True)
    except IndexError:
        return None

    """
    Each is approximately the timeframe divided by the max datapoints (100)

    Sample Calculations
    -------------------
    7 days * 24 hours / day * 60 min / hour / 100 = 100.8 minutes / point (floored to 100)
    1 hour * 60 min / hr * 60 sec / min / 100 points = 36 seconds / point
    5 minutes * 60 seconds / min / 100 points = 3 seconds / point 
    """
    
    if timeframe == "7 Days":
        rule = "100T"
        pad = False

    elif timeframe == "3 Days":
        rule = "43T"
        pad = False

    elif timeframe == "1 Day":
        rule = "14T"
        pad = False

    elif timeframe == "1 Hour":
        rule = "36S"
        pad = True
    elif timeframe == "5 Minutes":
        rule = "3S"
        pad = True
    else:
        rule = "3S"
        pad = True

    if pad:
        df = df.resample(rule).pad()
    else:
        df = df.resample(rule).mean()

    # Make sure that we do not send a dataframe that is longer then what the window
    # will handle
    if len(df) > 100:
        df = df.tail(100)

    return df
