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

from brewlab.user import init_df
from brewlab.connections import setup, activateArd, get_data
from brewlab.control import fermControl

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

SAMPLING_RATE = 5

def callback(df, filename, *largs):
    for ferm in fermenters:
        if ferm.active is True:
            row = get_data(ferm.id, ferm.serialCon)
            fermControl(ferm.serialCon, ferm.temp, row[3], ferm.auto)

            timestamp = datetime.datetime.now()
            df.loc[timestamp, ferm.name] = row

    df.to_csv(filename)

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

class MyScreenManager(ScreenManager):
    pass

class GraphScreen(Screen):

    def __init__(self, num_data_points=50, **kwargs):
        super(GraphScreen, self).__init__()
        self.tempplot = MeshLinePlot(color=[1, 0, 0, 1])
        self.pHplot = MeshLinePlot(color=[1, 0, 0, 1])
        self.DOplot = MeshLinePlot(color=[1, 0, 0, 1])
        self.level = []
        self._num_data_points = num_data_points
        self.xmin = 0
        self.xmax = num_data_points

        self.range = '1 Day'
        self.fermenter = 'Fermenter 1'

    def start(self):
        self.ids.temp.add_plot(self.tempplot)
        self.ids.pH.add_plot(self.pHplot)
        self.ids.DO.add_plot(self.DOplot)

        df, filename = init_df()
        self.main_callback = partial(callback, df, filename)
        self.df = df

        self.ids.start.disabled = True

        Clock.schedule_interval(self.get_value, SAMPLING_RATE)
        Clock.schedule_interval(self.main_callback, SAMPLING_RATE)

    def stop(self):
        try:
            Clock.unschedule(self.get_value)
            Clock.unschedule(self.main_callback)
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

        print(self.range)
        print(self.fermenter)

    def get_value(self, dt):
        self.tempplot.points = [(i, j) for i, j in enumerate(
            self.df[self.fermenter]['Temp (C)'])]

        self.pHplot.points = [(i, j) for i, j in enumerate(
            self.df[self.fermenter]['pH'])]

        self.DOplot.points = [(i, j) for i, j in enumerate(
            self.df[self.fermenter]['DO (mg/L)'])]

        self.tempplot.ymax = max(self.level)
        self.pHplot.ymax = max(self.level)
        self.DOplot.ymax = max(self.level)

class BrewLabApp(App):
    pass

if __name__ == '__main__':
    fermenters = setup()
    BrewLabApp().run()
