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
import sys
import numpy as np
import matplotlib.pyplot as plt

from configparser import ConfigParser
from unittest import mock

sys.path.insert(0, os.path.join(os.path.abspath('.'), 'src'))
import kinematics1


cstring = """
[schema]
n = 7

[kinematics]
cyclemarker1 = M5
cyclemarker2 = M6
leftthreshold = .17
rightthreshold = .23
"""

config = ConfigParser()
config.read_string(cstring)
test_array = np.sin(np.linspace(-2*np.pi, 3*np.pi, 40))

walk = mock.Mock()
walk.markers = np.repeat(test_array, 14).reshape((40, 14))
walk.dir = 0
walk.id = 1


def test_cycler():
    cyclemarkers = (10, 11), (12, 13)
    threshold = (.15, .17)
    cycler = kinematics1.Cycler(config)
    cycler.find_cycles(walk, cyclemarkers, threshold)


def test_kinematics():
    kine = kinematics1.Kinematics(config)
    kine.cycle_walks([walk, walk, walk, walk, walk ])
