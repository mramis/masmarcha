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
from json import load

from configparser import ConfigParser
from io import StringIO

import matplotlib.pyplot as plt

sys.path.insert(0, 'src')

from video import *

string_config = """
[paths]
schema = /home/mariano/masmarcha/schema7.json
"""

config = ConfigParser()
config.read_file(StringIO(string_config))

schema = load(open(config.get('paths', 'schema')))
path = '/home/mariano/Devel/masmarcha/src/material/VID_20180524_092057941.mp4'


def test_getrois():
    arr = np.ndarray((7, 2))
    fi = 10
    assert(get_regions(fi, arr, schema).size == len(schema['schema']*2*2) + 1)


def test_interprois():
    pre = np.hstack((0, np.arange(12)))
    cur = np.hstack((10, np.arange(12, 24)))
    dom = np.arange(pre[0] + 1, cur[0])
    arr = interpolate_lost_regions((pre, cur), schema)
    assert(arr.shape[0] == dom.size)




# def test_openvideo():
#     with open_video(path) as video:
#         assert(isinstance(video, cv2.VideoCapture))
#
#
# def test_markers():
#     with open_video(path) as video:
#         video.set(cv2.CAP_PROP_POS_FRAMES, 100)
#         ret, frame = video.read()
#         assert(ret == True)
#         assert(isinstance(frame, np.ndarray))
#         # testintg find_contours
#         contours = find_contours(frame)
#         assert(isinstance(contours, list))
#         # testing markers_center
#         center = marker_center(contours[0])
#         assert(isinstance(center, tuple))
#         # testing get_centers
#         markers = get_markers(frame)
#         assert(isinstance(markers, np.ndarray))
#
#
# def test_explorer():
#     walks = find_walks(path, config)
#     for i, interval in enumerate(walks):
#         assert(isinstance(interval, tuple))
#         assert(len(interval) == 2)
#         if i == 1:
#             walks.close()
