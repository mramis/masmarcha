#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2019  Mariano Ramis

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

import time

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.logger import Logger


class SectionsControl(TabbedPanel):
    mode = StringProperty("video")
    do_default_tab = False

    def on_current_tab(self, instance, tab):
        u"""Cuando se selecciona la pestaña, activa contenido específico."""
        tab.content.setVariables()


class SubSection(GridLayout):

    def setVariables(self):
        return NotImplemented

    def writeConfig(self):
        with open(self.config.get("paths", "configfile"), "w") as fh:
            self.config.write(fh)


class VideoSubSection(SubSection):
    devices = {"webcam": "0", "usb_camera": "2"}

    def setVariables(self):
        u"""."""
        self.setDevice()
        self.setVideoName()

    def setDevice(self, dev=None):
        u"""."""
        default = self.config.get("video", "device")
        if dev is None:
            self.config.set("current", "source", self.devices[default])
        else:
            self.config.set("current", "source", self.devices[dev])
        self.writeConfig()

    def setVideoName(self, name=None):
        u"""."""
        if name is None:
            name = time.strftime("%d%m%y%H%M%S")
        self.ids.videoname.text = name
        self.config.set("video", "filename", "%s.avi" % name)
        self.writeConfig()


class ExplorerSubSection(SubSection):

    def set_config(self):
        u"""."""
        source = self.config.get("video", "filepath")
        self.config.set("current", "source", source)
        self.write_config()


class KinematicsSubSection(SubSection):

    def set_variables(self):
        u"""."""
        print(self)
