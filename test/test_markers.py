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

from src.core.array import *
from src.core.regions import *
from src.core.markers import *
from src.core.settings import config

data = np.array((
    np.arange(100),
    np.repeat(50, 100),
    np.arange(100),
    np.repeat(100, 100),
    np.arange(100),
    np.repeat(200, 100),
    np.arange(100),
    np.repeat(250, 100),
    np.arange(100),
    np.repeat(400, 100),
    np.arange(100),
    np.repeat(450, 100),
    np.arange(100),
    np.repeat(500, 100),
), dtype=int).transpose()


def adapt_data(data):
    full = np.random.choice((True, False))
    if full == False:
        amount = np.random.choice((True, False))
        if amount == True:
            data = np.concatenate((data, data[:4]))
        else:
            data = data[:6]
    return full, data

def insert_random(array, data):
    pos = np.random.randint(0, 100)
    for row in data:
        full, row = adapt_data(row)
        array.addFrameData((pos, full, row))
        pos += 1


def test_markers_identifier():

    warray = WalkArray()
    insert_random(warray, data)
    warray.close()

    config.set("walk", "roiwidth", "10")
    config.set("walk", "roiheight", "10")

    regions = Regions(warray, config)
    regions.build()

    plt.plot(*warray.getView(["markers", "region0", "m1"]).transpose(), "ro")
    plt.plot(*warray.getView(["regions", "region0", "p0"]).transpose(), "bs")
    plt.plot(*warray.getView(["regions", "region0", "p1"]).transpose(), "gs")

    identifier = MarkersIdentifier(warray)
    identifier.identify()

    plt.plot(*warray.getView(["markers", "region0", "m1"]).transpose(), "kx")

    plt.show()
    plt.close()


def test_sort_foot():

    warray = WalkArray()
    insert_random(warray, data)
    warray.close()

    sorter = MarkersFootSorter(warray)
    sorter.sort()


def test_markers_interpolation():

    warray = WalkArray()
    insert_random(warray, data)
    warray.close()

    regions = Regions(warray, config)
    regions.build()

    plt.plot(*warray.getView(["markers", "region0", "m1"]).transpose(), "ro")
    plt.plot(*warray.getView(["regions", "region0", "p0"]).transpose(), "bs")
    plt.plot(*warray.getView(["regions", "region0", "p1"]).transpose(), "gs")

    identifier = MarkersIdentifier(warray)
    identifier.identify()

    interpolator = MarkersInterpolator(warray)
    interpolator.interpolate()

    plt.plot(*warray.getView(["markers", "region0", "m1"]).transpose(), "k<")

    plt.show()
    plt.close()


def test_markers():

    warray = WalkArray()
    insert_random(warray, data)
    warray.close()

    regions = Regions(warray, config)
    regions.build()
    
    markers = Markers(warray)
    markers.fix()

    plt.plot(*warray.getView(["markers", "region0", "m1"]).transpose(), "k<")

    plt.show()
    plt.close()
