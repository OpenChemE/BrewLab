from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
import numpy as np
from kivy.app import App
from kivy.garden.graph import MeshLinePlot
from kivy.clock import Clock
from collections import namedtuple
import serial
import os

from brewlab.connections import setup
from brewlab.user import fermChoose

if os.environ.get("MODE") == "dev":
    from brewlab import fakeSerial as serial

class MenuScreen(Screen):

    def get_inputs(self):

        if self.ids.ferm1.state is "down":
            fermenters[0] = fermenters[0]._replace(
                active=True, temp=self.ids.f1Temp.value)

        if self.ids.ferm2.state is "down":
            fermenters[1] = fermenters[1]._replace(
                active=True, temp=self.ids.f2Temp.value)

        if self.ids.ferm3.state is "down":
            fermenters[2] = fermenters[2]._replace(
                active=True, temp=self.ids.f3Temp.value)

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

    def start(self):
        self.ids.temp.add_plot(self.tempplot)
        self.ids.pH.add_plot(self.pHplot)
        self.ids.DO.add_plot(self.DOplot)
        Clock.schedule_interval(self.get_value, 1)

    def stop(self):
        Clock.unschedule(self.get_value)

    def get_value(self, dt):
        self.level.append(np.random.random_sample()*100)
        self.tempplot.points = [(i, j/5) for i, j in enumerate(self.level)]
        self.pHplot.points = [(i, j/5) for i, j in enumerate(self.level)]
        self.DOplot.points = [(i, j/5) for i, j in enumerate(self.level)]

        self.tempplot.ymax = max(self.level)
        self.pHplot.ymax = max(self.level)
        self.DOplot.ymax = max(self.level)

class BrewLabApp(App):
    pass

if __name__ == '__main__':
    fermenters = setup()
    BrewLabApp().run()
