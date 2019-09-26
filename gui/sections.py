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

import os
import time

from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty


class Sections(TabbedPanel):
    mode = StringProperty("video")
    do_default_tab = False

    def on_current_tab(self, instance, tab):
        u"""Cuando se selecciona la pestaña, activa contenido específico."""
        tab.content.setTabbState()


class SubSection(GridLayout):

    def setTabbState(self):
        return NotImplemented

    def writeConfig(self):
        with open(self.config.get("paths", "configfile"), "w") as fh:
            self.config.write(fh)


class VideoSubSection(SubSection):
    devices = {"webcam": "0", "usb_camera": "2"}

    def setTabbState(self):
        u"""."""
        self.setDevice()
        self.setVideoName()
        self.setEnableDisabled()

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
            name = "%s.avi" % time.strftime("%d%m%y%H%M%S")
        else:
            name = "%s.avi" % name.replace(' ', '_')
        self.ids.videoname.text = name
        self.config.set("video", "filename", name)
        self.writeConfig()

    def setEnableDisabled(self):
        # Enabled Buttons
        self.vu_buttons["record"].disabled = False
        self.vu_buttons["play"].disabled = False
        self.vu_buttons["stop"].disabled = False
        # Disabled Buttons
        self.vu_buttons["back"].disabled = True
        self.vu_buttons["next"].disabled = True


class ExplorerSubSection(SubSection):

    def setTabbState(self):
        u"""."""
        self.setFilepath()
        self.setEnableDisabled()

    def setFilepath(self):
        u"""."""
        dirpath = self.config.get("paths", "video")
        filename = self.config.get("video", "filename")
        self.config.set("current", "source", os.path.join(dirpath, filename))
        self.writeConfig()

    def setEnableDisabled(self):
        # Enabled Buttons
        self.vu_buttons["play"].disabled = False
        self.vu_buttons["stop"].disabled = False
        # Disabled Buttons
        self.vu_buttons["record"].disabled = True
        self.vu_buttons["back"].disabled = True
        self.vu_buttons["next"].disabled = True


class KinematicsSubSection(SubSection):

    def setTabbState(self):
        u"""."""
        pass
