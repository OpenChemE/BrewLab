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
    filename = "data/" + str(today)+ "_data.csv"

    return df, filename


def resample_data(filename, timeframe):
    """
    Reads data from the CSV and formats it to the users request. 
    """

    # Read data from generated csv
    df = pd.read_csv(filename, index_col=0,
                     header=[0, 1], parse_dates=True)

    # Each is approximately the timeframe divided by the max datapoints (100)
    if timeframe == "1 Day":
        rule = "15T"
    elif timeframe == "3 Days":
        rule = "45T"
    elif timeframe == "7 Days":
        rule = "100T"
    elif timeframe == "1 Hour":
        rule = "36S"
    elif timeframe == "5 Minutes":
        rule = "5S"
    else:
        rule = "5S"

    df = df.resample(rule).mean()

    # Make sure that we do not send a dataframe that is longer then what the window
    # will handle
    if len(df) > 100:
        df = df.tail(100)

    return df
