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
import sys
from configparser import ConfigParser
from kivy.app import App

sys.path.insert(0, 'src')

import masmarchaapp

string_config = """
[paths]
config = test/masmarchaconfig
sourcedir =

[explorer]
dilate = 0
threshold = 240
extrapixel = 35
roimethod = Banda

[display]
framewidth = 640
frameheight = 480

[camera]
fpscorrection = 0

[cycles]
threshold = 0.8
cyclemarker1 = M5
cyclemarker2 = M6

[plots]
aspect1 = 0.65
aspect2 = 0.3
dpi = 80
"""

config = ConfigParser()
config.read_string(string_config)


def test_main():
    app = masmarchaapp.MasMarchaApp('test/masmarchaconfig')
    app.run()
