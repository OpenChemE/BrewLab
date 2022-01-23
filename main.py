from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
import numpy as np
from kivy.app import App
from kivy.garden.graph import Graph,MeshLinePlot
from kivy.clock import Clock
from collections import namedtuple
import serial
import os
import datetime
from functools import partial
import concurrent.futures
import threading
from kivy.logger import Logger

from brewlab.user import init_df, resample_data
from brewlab.connections import ardCon, setup, activateArd, get_data
from brewlab.control import fermControl

if os.environ.get("MODE") == "dev":
    Logger.warning("App: Activating development mode...")
    from brewlab import fakeSerial as serial

SAMPLING_RATE = 10

class MenuScreen(Screen):
    """
    MenuScreen is the first screen entered in the app for setting up Fermenters. 
    """

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

    def execute(self):
        """
        Retrieves button states for each fermenter and activates the arduino if active
        """

        if self.ids.ferm1.state is "down":
            fermenters[0] = fermenters[0]._replace(
                active=True, temp=self.ids.f1Temp.value)
            SERIAL_CON.write('1'.encode())
        else: 
            SERIAL_CON.write('0'.encode())

        if self.ids.ferm2.state is "down":
            fermenters[1] = fermenters[1]._replace(
                active=True, temp=self.ids.f2Temp.value)
            SERIAL_CON.write('1'.encode())
        else:
            SERIAL_CON.write('0'.encode())

        if self.ids.ferm3.state is "down":
            fermenters[2] = fermenters[2]._replace(
                active=True, temp=self.ids.f3Temp.value)
            SERIAL_CON.write('1'.encode())
        else:
            SERIAL_CON.write('0'.encode())

class ConfigScreen(Screen):
    """
    Changing settings after data collection has started.
    """

    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)

    def on_pre_enter(self, **kwargs):
        """
        Retrieve state for each fermenter on entry to screen
        """
        
        if fermenters[0].active is True:
            self.ids.f1Temp.value = fermenters[0].temp
        
        if fermenters[1].active is True:
            self.ids.f2Temp.value = fermenters[1].temp
        
        if fermenters[2].active is True:
            self.ids.f3Temp.value = fermenters[2].temp

        if fermenters[0].auto is True:
            self.ids.ferm1Auto.state = "down"
        else:
            self.ids.ferm1Man.state = "down"

        if fermenters[1].auto is True:
            self.ids.ferm1Auto.state = "down"
        else:
            self.ids.ferm1Man.state = "down"

        if fermenters[2].auto is True:
            self.ids.ferm1Auto.state = "down"
        else:
            self.ids.ferm1Man.state = "down"

    def press(self, *args):
        """
        ConfigScreen.press handles button pressing in the config screen
        """
        button = args[0]

        if button.group == "f1Config" and button.text != "Auto":
            fermenters[0] = fermenters[0]._replace(
                auto=False)
            
            self.ids.p1on.disabled = False
            self.ids.p1off.disabled = False
            self.ids.p1off.state = "down"

        elif button.group == "f2Config" and button.text != "Auto":
            fermenters[1] = fermenters[1]._replace(
                auto=False)

            self.ids.p2on.disabled = False
            self.ids.p2off.disabled = False
            self.ids.p2off.state = "down"

        elif button.group == "f3Config" and button.text != "Auto":
            fermenters[2] = fermenters[2]._replace(
                auto=False)

            self.ids.p3on.disabled = False
            self.ids.p3off.disabled = False
            self.ids.p3off.state = "down"

        elif button.group == "f1Config":
            fermenters[0] = fermenters[0]._replace(
                auto=True)

            self.ids.p1on.disabled = True
            self.ids.p1off.disabled = True
            self.ids.p1off.state = "normal"
            self.ids.p1on.state = "normal"

        elif button.group == "f2Config":
            fermenters[1] = fermenters[1]._replace(
                auto=True)

            self.ids.p2on.disabled = True
            self.ids.p2off.disabled = True
            self.ids.p2off.state = "normal"
            self.ids.p2on.state = "normal"

        elif button.group == "f3Config":
            fermenters[2] = fermenters[2]._replace(
                auto=True)

            self.ids.p3on.disabled = True
            self.ids.p3off.disabled = True
            self.ids.p3off.state = "normal"
            self.ids.p3on.state = "normal"

    def pump(self, *args):
        """
        Turns on/off pumps for each fermenter
        """
        button = args[0]

        if button.group == "p1Status" and button.text == "ON":
            SERIAL_CON.write('PT1'.encode())
            Logger.info("Pump: Turning on Pump 1")
        elif button.group == "p2Status" and button.text == "ON":
            SERIAL_CON.write('PT2'.encode())
            Logger.info("Pump: Turning on Pump 2")
        elif button.group == "p3Status" and button.text == "ON":
            SERIAL_CON.write('PT3'.encode())
            Logger.info("Pump: Turning on Pump 3")
        elif button.group == "p1Status":
            SERIAL_CON.write('PF1'.encode())
            Logger.info("Pump: Turning off Pump 1")
        elif button.group == "p2Status":
            SERIAL_CON.write('PF2'.encode())
            Logger.info("Pump: Turning off Pump 2")
        elif button.group == "p3Status":
            SERIAL_CON.write('PF3'.encode())
            Logger.info("Pump: Turning off Pump 3")

    def get_config(self):
        """
        Updates settings on exiting Config Screen
        """
        fermenters[0] = fermenters[0]._replace(temp=self.ids.f1Temp.value)
        fermenters[1] = fermenters[1]._replace(temp=self.ids.f2Temp.value)
        fermenters[2] = fermenters[2]._replace(temp=self.ids.f3Temp.value)

class MyScreenManager(ScreenManager):
    """
    Handles Screen Changes
    """
    pass

class GraphScreen(Screen):
    """
    Handles data collection and visualization
    """

    def __init__(self, num_data_points=100, **kwargs):
        super(GraphScreen, self).__init__()
        self.tempplot = MeshLinePlot(color=[1, 0, 0, 1])
        self.pHplot = MeshLinePlot(color=[1, 0, 0, 1])
        self.DOplot = MeshLinePlot(color=[1, 0, 0, 1])
        
        self._num_data_points = num_data_points
        self.xmin = 0
        self.xmax = num_data_points

        self.range = '5 Minutes'
        self.fermenter = 'Fermenter 1'
        self.filename = None

    def callback(self, df, filename, *largs):
        """
        Collects data from each active fermenter
        """

        # Timestamp represents the time when data is requested
        timestamp = datetime.datetime.now()

        row = get_data(SERIAL_CON)

        # Need to reorder the row to fit the dataframe
        for ferm in fermenters:
            if ferm.active:
                i = 0
                temp = row[i]
                ph = row[i+1]
                do = row[i+2]

                fermControl(SERIAL_CON, ferm, temp)

                time = datetime.datetime.now()
                df.loc[timestamp, ferm.name] = [time, temp, ph, do]

                i += 3

        df.to_csv(filename)

    def start(self):
        """
        Schedules callback and data plotting and creates dataframe
        """
        self.ids.temp.add_plot(self.tempplot)
        self.ids.pH.add_plot(self.pHplot)
        self.ids.DO.add_plot(self.DOplot)

        df, filename = init_df()
        self.main_callback = partial(self.callback, df, filename)

        self.filename = filename

        self.ids.start.disabled = True

        Logger.info("App: Starting data collection . . .")
        Clock.schedule_interval(self.main_callback, SAMPLING_RATE)
        Clock.schedule_interval(self.get_value, SAMPLING_RATE*2)

    def stop(self):
        """
        Stops data collection and saves file one last time
        """
        try:
            Clock.unschedule(self.get_value)
            Clock.unschedule(self.main_callback)
            Logger.info("App: Stopping data collection")
        except AttributeError:
            pass
        finally:
            self.ids.start.disabled = False

    def press(self, *args):
        """
        GraphScreen.press handles button pressing in GraphScreen for Range and active Fermenter
        """
        button = args[0]
        state = args[1]

        if button.group == "time" and state == "down":
            self.range = button.text
        elif button.group == "fermenter" and state == "down":
            self.fermenter = button.text
        
        self.get_value(SAMPLING_RATE)

    def get_value(self, dt):
        """
        Samples and plots data according to user input
        """

        if self.filename is None:
            return

        df = resample_data(self.filename, self.range)

        self.tempplot.points = [(i, j) for i, j in enumerate(
            df[self.fermenter]['Temp (C)'])]

        self.pHplot.points = [(i, j) for i, j in enumerate(
            df[self.fermenter]['pH'])]

        self.DOplot.points = [(i, j) for i, j in enumerate(
            df[self.fermenter]['DO (mg/L)'])]

        if self.tempplot.points:
            self.tempplot.ymax = max(df[self.fermenter]['Temp (C)'])
        if self.pHplot.points:
            self.pHplot.ymax = max(df[self.fermenter]['pH'])
        if self.DOplot.points:
            self.DOplot.ymax = max(df[self.fermenter]['DO (mg/L)'])

class BrewLabApp(App):
    """
    Kivy App Object
    """
    pass

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(setup)
        fermenters = future.result()

    SERIAL_CON = ardCon('COM4')

    BrewLabApp().run()
