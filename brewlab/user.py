import serial
import os
import datetime
from time import sleep
import pandas as pd
import numpy as np

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

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
