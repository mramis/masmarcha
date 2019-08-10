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

from .array import WalkArray
from .regions import Regions
from .markers import Markers


class Walk(object):
    __counter = 0

    def __init__(self, config):
        Walk.__counter += 1
        self.id = Walk.__counter
        self.warray = WalkArray()
        self.markers = Markers(self.warray)
        self.regions = Regions(self.warray, config)

    def __str__(self):
        return "Caminata {}".format(self.id)

    @classmethod
    def num_of_walks(cls):
        return cls.__counter

    @classmethod
    def restart(cls):
        cls.__counter = 0

    def insert(self, pos, full, framedata):
        self.warray.addFrameData((pos, full, framedata))

    def stop(self):
        self.warray.close()

    def process(self):
        u"""."""
        self.regions.build()
        self.markers.fix()
