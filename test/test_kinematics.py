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

from configparser import ConfigParser
from unittest import mock

sys.path.insert(0, os.path.join(os.path.abspath('.'), 'src'))
import kinematics


cstring = """
[schema]
n = 7
leg = 3,4
foot = 5,6
tight = 1,2

order_joints = hip,knee,ankle
order_segments = tight,leg,foot

[kinematics]
nfixed = 100
maxcycles = 50
cyclemarker1 = M5
cyclemarker2 = M6
leftthreshold = .17
rightthreshold = .23
filter_by_duration = False

leftlength = 0.28
rightlength = 0.28

[camera]
fps = 60
fpscorrection = 1
"""

config = ConfigParser()
config.read_string(cstring)


nsample = 100
testarray = np.sin(np.linspace(-2*np.pi, 3*np.pi, nsample))
mockarray = np.ndarray((nsample, 14))

for col in range(14):
    mockarray[:, col] = testarray + np.random.random()

walk = mock.Mock()
walk.markers = mockarray
walk.dir = 0
walk.id = 1

#
# def test_schema():
#     schema = kinematics1.Schema(config)
#     schema.get_marker(walk.markers, 0)
#     schema.get_marker(np.array((walk.markers, walk.markers)), 6)
#     schema.get_segment(walk.markers, 'leg')
# #


def test_cycler():
    cyclemarkers = (10, 11), (12, 13)
    threshold = (.15, .17)
    cycler = kinematics.Cycler(config)
    cycler.find_cycles(walk, cyclemarkers, threshold)
    cycler.stop()
    cycler.filter_by_duration()


# def test_kinematics():
#     kine = kinematics1.Kinematics(config)
#     kine.cycle_walks([walk, walk, walk, walk, walk ])
#     kine.calculate_angles()
#     kine.calculate_stp()
#
# def test_angles():
#     nsample = np.random.randint(0, 50)
#     segments = mockarray[:, :6]
#     segments = np.repeat(segments, nsample).reshape((nsample,) + segments.shape)
#     direction = np.random.randint(0, 2 , nsample)
#
#     anglesCalc = kinematics1.Angles()
#     canonical = anglesCalc.canonicalX(direction)
#     anglesCalc.calculate(segments, direction)

# def test_stp():
#     nsample = np.random.randint(0, 50)
#     markers = np.random.random((nsample, 100, 14))
#     direction = np.random.randint(0, 2 , nsample)

    # cyclessv = np.random.random((nsample, 6))
    # duration = np.random.random((nsample))
    # stride = np.random.random((nsample))

    # stp = kinematics1.SpatioTemporal(config)
    # realdistances = stp._legdistance(direction)
    # pxtom = stp._scale(markers, realdistances)
    # print(stp.stride(markers, pxtom))

    # b = stp.temporal(60, cyclessv)
    # c = stp.velocity(duration, stride)
    # det = np.ndarray((nsample, 9))
    # det[:, 1:6] = np.array(b).transpose()
    # det[:, 6] = a
    # det[:, 7:] = np.array(c).transpose()
