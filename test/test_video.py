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

import numpy as np
import matplotlib.pyplot as plt

from src.core.video import Video, Frame, View
from src.core.settings import config, SCHEMA as schema

path = "/home/mariano/Descargas/VID_20181115_183356560.mp4"
badpath = "/home/mariano/Descargas/marcha(verlekar).pdf"


def test_video():
    video = Video(config, schema)


def test_load_video():
    video = Video(config, schema)
    video.open(path)
    try:
        video.open(badpath)
    except Exception:
        print("[Exception badfile raised]", end=" ")


def test_read():
    global frame
    video = Video(config, schema)
    video.open(path)
    ret, pos, frame = video.read()
    assert(ret)
    assert(pos == 1)
    assert(isinstance(frame, Frame))


def test_frame():
    n, markers = frame.getMarkersPositions()


def test_frame_transform():
    frame.vflip()
    frame.resize()
    plt.imshow(frame.frame)
    plt.show()


def test_frame_draw():
    n, markers = frame.getMarkersPositions()
    frame.vflip()
    frame.drawText(n)
    frame.drawMarkers(markers)
    regions = np.random.randint(0, 100, (3, 2, 2))
    condition = np.array([0, 1, 0])
    frame.drawRegions(regions, condition)
    plt.imshow(frame.frame)
    plt.show()


def test_explorer():
    global walk
    video = Video(config, schema)
    video.open(path)
    for pos, walk in video.searchForWalks():
        print('[%s]' % walk, end=" ")
        break


def test_view():
    video = Video(config, schema)
    video.open(path)
    video.setPosition(walk.startframe + 100)
    ret, pos, frame = video.read()

    view = View(config, schema)
    view.drawUnidentifiedMarkers(frame)
    plt.imshow(frame.frame)
    plt.show()

    walk.process()
    view.drawWalkMarkers(frame, walk)
    plt.imshow(frame.frame)
    plt.show()


def test_view_play():
    video = Video(config, schema)
    video.open(path)

    view = View(config, schema)
    config.set("video", "startframe", "%s" % str(walk.startframe + 100))
    config.set("video", "endframe", "%s" % str(walk.startframe + 110))
    for frame in view.player(video):
        plt.imshow(frame.frame)
        plt.show()

    for frame in view.player(video, walk):
        plt.imshow(frame.frame)
        plt.show()
