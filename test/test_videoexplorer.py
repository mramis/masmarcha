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

from src.videoexplorer import Explorer
from src.settings import app_config


class VideoMock(object):
    size = 30 + 60  # limite de corte

    def __init__(self):
        self.currentframe = 0
        self.videosize = self.size

    def read_frame(self):
        isframe = True
        if self.currentframe == self.size:
            isframe = False
        to_return = (isframe, self.currentframe, None)
        self.currentframe += 1
        return to_return

    def contours(self, frame):
        contours = []
        random_contours = np.random.randint(0, 14)
        # Para poder inciar y finalizar la caminata.
        if self.currentframe == 5 or self.currentframe == 25:
            random_contours = 7
        # Este es el valor que hace saltar la cláusula de EFL
        if self.currentframe > 29:
            random_contours = 0

        for __ in range(random_contours):
            contours.append(None)
        return len(contours), contours

    def centers(self, contours):
        centers = []
        for c in contours:
            point = np.random.randint(0, 640, (1, 2))
            centers.append(point)
        return np.array(centers)

def test_init():
    Explorer(app_config)

def test_findWalks():
    exp = Explorer(app_config)
    exp.findWalks(VideoMock())
    print(exp.walks[0].markers.shape)

    print("Modificando parámetros de limite tolerante de cuadros")
    app_config.set("walk", "emptyframelimit", "0")

    exp = Explorer(app_config)
    exp.findWalks(VideoMock())
    print(exp.walks[0].markers.shape)
