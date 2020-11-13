from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
import numpy as np
from kivy.app import App
from kivy.garden.graph import MeshLinePlot
from kivy.clock import Clock
from collections import namedtuple
import serial
import os
import datetime
from functools import partial
import concurrent.futures
from kivy.logger import Logger

from brewlab.user import init_df, resample_data
from brewlab.connections import setup, activateArd, get_data
from brewlab.control import fermControl

if os.environ.get("MODE") == "dev":
    Logger.warning("App: Activating development mode...")
    from brewlab import fakeSerial as serial

SAMPLING_RATE = 5

class MenuScreen(Screen):

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

    def execute(self):

        if self.ids.ferm1.state is "down":
            fermenters[0] = fermenters[0]._replace(
                active=True, temp=self.ids.f1Temp.value)

        if self.ids.ferm2.state is "down":
            fermenters[1] = fermenters[1]._replace(
                active=True, temp=self.ids.f2Temp.value)

        if self.ids.ferm3.state is "down":
            fermenters[2] = fermenters[2]._replace(
                active=True, temp=self.ids.f3Temp.value)

        for ferm in fermenters:
            activateArd(ferm)

class ConfigScreen(Screen):

    def __init__(self, **kwargs):
        super(ConfigScreen, self).__init__(**kwargs)

    def on_pre_enter(self, **kwargs):
        
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
        button = args[0]

        if button.group == "p1Status" and button.text == "ON":
            fermenters[0].serialCon.write('PT'.encode())
            Logger.info("Pump: Turning on Pump 1")
        elif button.group == "p2Status" and button.text == "ON":
            fermenters[1].serialCon.write('PT'.encode())
            Logger.info("Pump: Turning on Pump 2")
        elif button.group == "p3Status" and button.text == "ON":
            fermenters[2].serialCon.write('PT'.encode())
            Logger.info("Pump: Turning on Pump 3")
        elif button.group == "p1Status":
            fermenters[0].serialCon.write('PF'.encode())
            Logger.info("Pump: Turning off Pump 1")
        elif button.group == "p1Status":
            fermenters[1].serialCon.write('PF'.encode())
            Logger.info("Pump: Turning off Pump 2")
        elif button.group == "p1Status":
            fermenters[2].serialCon.write('PF'.encode())
            Logger.info("Pump: Turning off Pump 3")

    def get_config(self):
        fermenters[0] = fermenters[0]._replace(temp=self.ids.f1Temp.value)
        fermenters[1] = fermenters[1]._replace(temp=self.ids.f2Temp.value)
        fermenters[2] = fermenters[2]._replace(temp=self.ids.f3Temp.value)

class MyScreenManager(ScreenManager):
    pass

class GraphScreen(Screen):

    def __init__(self, num_data_points=100, **kwargs):
        super(GraphScreen, self).__init__()
        self.tempplot = MeshLinePlot(color=[1, 0, 0, 1])
        self.pHplot = MeshLinePlot(color=[1, 0, 0, 1])
        self.DOplot = MeshLinePlot(color=[1, 0, 0, 1])

        self.iter = 0
        
        self._num_data_points = num_data_points
        self.xmin = 0
        self.xmax = num_data_points

        self.range = '5 Minutes'
        self.fermenter = 'Fermenter 1'

    def callback(self, iter, df, filename, *largs):

        # Timestamp represents the time when data is requested
        timestamp = datetime.datetime.now()

        for ferm in fermenters:
            if ferm.active is True:
                # Request data from fermenter
                row = get_data(ferm.id, ferm.serialCon)

                # When all data is collected proceed
                if row is not None:
                    fermControl(ferm.serialCon, ferm.temp, row[3], ferm.auto)

                    row[0] = datetime.datetime.now()
                    df.loc[timestamp, ferm.name] = row

        self.iter += 1
        df.to_csv(filename)

    def start(self):
        self.ids.temp.add_plot(self.tempplot)
        self.ids.pH.add_plot(self.pHplot)
        self.ids.DO.add_plot(self.DOplot)
        self.iter = 0

        df, filename = init_df()
        self.main_callback = partial(self.callback, self.iter, df, filename)

        self.filename = filename

        self.ids.start.disabled = True

        Logger.info("App: Starting data collection . . .")
        Clock.schedule_interval(self.main_callback, SAMPLING_RATE)
        Clock.schedule_interval(self.get_value, SAMPLING_RATE)

    def stop(self):
        try:
            Clock.unschedule(self.get_value)
            Clock.unschedule(self.main_callback)
            Logger.info("App: Stopping data collection")
        except AttributeError:
            pass
        finally:
            self.ids.start.disabled = False

    def press(self, *args):
        button = args[0]
        state = args[1]

        if button.group == "time" and state == "down":
            self.range = button.text
        elif button.group == "fermenter" and state == "down":
            self.fermenter = button.text
        
        self.get_value(SAMPLING_RATE)

    def get_value(self, dt):

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
    pass

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(setup)
        fermenters = future.result()

    BrewLabApp().run()
