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
from src.core.settings import config


# NOTE: Test data son las trayectorias de 7 marcadores durante 20 cuadros.
test_data = np.zeros((20, 7*2))
test_data_enter = np.array((
    np.arange(20),  # x
    np.random.normal(loc=1, scale=0.2, size=20))  # y
)
test_data[:, (0, 1)] = test_data_enter.transpose()


def test_regions_calculator():
    print()

    warray = WalkArray()
    for i, data in enumerate(test_data):
        warray.addFrameData((i, True, data))

    warray.close()

    markers = warray.getView(["markers", "all"])
    assert(np.shares_memory(markers, warray.array))
    print(warray.array[9])

    calculator = RegionsCalculator(warray, config)
    calculator.calculate()
    print(warray.array[9])

    plt.plot(warray.getView(["markers", "region0", "m0"])[:, 0])
    plt.plot(warray.getView(["regions", "region0", "p0"])[:, 0])
    plt.plot(warray.getView(["regions", "region0", "p1"])[:, 0])
    plt.show()
    plt.close()


def test_regions_supervisor():
    print()

    warray = WalkArray()
    for i, data in enumerate(test_data[:4]):
        warray.addFrameData((i, True, data))

    for i, data in enumerate(test_data[4:6]):
        warray.addFrameData((i, True, data * 2))

    for i, data in enumerate(test_data[6:]):
        warray.addFrameData((i, True, data))

    warray.close()

    calculator = RegionsCalculator(warray, config)
    calculator.calculate()

    config.set("walk", "surfaceerror", "0.4")
    config.set("walk", "centererror", "0.4")

    supervisor = RegionsSupervisor(warray, config)
    supervisor.supervise()

    print(warray.getView(["indicators", "region0"]))


def test_regions_interpolator():
    print()

    warray = WalkArray()
    for i, data in enumerate(test_data[:4]):
        warray.addFrameData((i, True, data))

    for i, data in enumerate(test_data[4:6]):
        warray.addFrameData((i, False, data[:6]))

    for i, data in enumerate(test_data[6:]):
        warray.addFrameData((i, True, data))

    warray.close()

    calculator = RegionsCalculator(warray, config)
    calculator.calculate()

    interpolator = RegionsInterpolator(warray)
    interpolator.interpolate()

    plt.plot(warray.getView(["markers", "region0", "m0"])[:, 0])
    plt.plot(warray.getView(["regions", "region0", "p0"])[:, 0])
    plt.plot(warray.getView(["regions", "region0", "p1"])[:, 0])
    plt.show()
    plt.close()


def test_regions():

    print()

    warray = WalkArray()
    for i, data in enumerate(test_data):
        warray.addFrameData((i, True, data))

    warray.close()

    regions = Regions(warray, config)
    regions.build()
