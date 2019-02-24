#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2018  Mariano Ramis

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from time import sleep
from queue import Queue
from threading import Thread, Event

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, DictProperty
from kivy.core.window import Window

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

from video import Explorer
from paths import Manager

Window.size = (1280, 1024)

class MasMarchaApp(App):

    def __init__(self):
        super().__init__()
        self.explorer = Explorer(self.config)
        self.pathmanager = Manager()

    def build_config(self, config):
        config.add_section('paths')
        config.set('paths', 'app', self.pathmanager.app)
        config.set('paths', 'normal_',
            os.path.join(config.get('paths', 'app'), 'normal'))
        config.set('paths', 'normal_stp',
            os.path.join(config.get('paths', 'normal_'), 'stp.csv'))
        config.set('paths', 'normal_rom',
            os.path.join(config.get('paths', 'normal_'), 'rom.csv'))
        config.set('paths', 'normal_hip',
            os.path.join(config.get('paths', 'normal_'), 'hip.csv'))
        config.set('paths', 'normal_knee',
            os.path.join(config.get('paths', 'normal_'), 'knee.csv'))
        config.set('paths', 'normal_ankle',
            os.path.join(config.get('paths', 'normal_'), 'ankle.csv'))

        config.add_section('explorer')
        config.set('explorer', 'dilate', 'False')
        config.set('explorer', 'threshold', '240')

        config.add_section('walk')
        config.set('walk', 'roiwidth', '125')
        config.set('walk', 'roiheight', '35')

        config.add_section('video')
        config.set('video', 'delay', '.1')
        config.set('video', 'framewidth', '640')
        config.set('video', 'frameheight', '480')

        config.add_section('camera')
        config.set('camera', 'fps', '60')
        config.set('camera', 'fpscorrection', '1')

        config.add_section('kinematics')
        config.set('kinematics', 'stpsize', '6')
        config.set('kinematics', 'maxcycles', '50')
        config.set('kinematics', 'llength', '0.28')
        config.set('kinematics', 'rlength', '0.28')
        config.set('kinematics', 'anglessize', '100')
        config.set('kinematics', 'lthreshold', '3.2')
        config.set('kinematics', 'rthreshold', '3.2')
        config.set('kinematics', 'cyclemarker1', 'M5')
        config.set('kinematics', 'cyclemarker2', 'M6')

        config.add_section('schema')
        config.set('schema', 'n', '7')
        config.set('schema', 'r', '3')
        config.set('schema', 'leg', '3,4')
        config.set('schema', 'foot', '5,6')
        config.set('schema', 'tight', '1,2')
        config.set('schema', 'markersxroi', '0,1/2,3/4,5,6')
        config.set('schema', 'order_segments', 'tight,leg,foot')
        config.set('schema', 'order_joints', 'hip,knee,ankle')

        config.add_section('plots')
        config.set('plots', 'dpi', '80')
        config.set('plots', 'textsize', '16')
        config.set('plots', 'titlesize', '23')
        config.set('plots', 'chartwidth', '8')
        config.set('plots', 'chartheight', '5')
        config.set('plots', 'tablewidth', '12')
        config.set('plots', 'tableheight', '5')
        config.set('plots', 'subtitlesize', '18')
        config.set('plots', 'standardeviation', '2')
        config.set('plots', 'cell_index_width', '0.3')
        config.set('plots', 'cell_normal_width', '0.25')

    def build(self):
        u"""Construye la interfaz gráfica."""
        return MainFrame()


class MainFrame(GridLayout):
    pass


class Session(GridLayout):

    def session_data_collect(self):
        for i in self.ids.items():
            print(i)
