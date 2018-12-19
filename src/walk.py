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

from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt



class Walk(object):

    def __init__(self, config, schema):
        self.cfg = config
        self.sch = schema
        self._regions = defaultdict(list)
        self._iregions = defaultdict(list)

    def interpolate(self, incp_indexes, full_indexes, data):
        u"""Modifica con valores interpolados el arreglo principal."""
        interp = [np.interp(incp_indexes, full_indexes, arr) for arr in data]
        return np.array(interp)

    def calc_regions(self, markers, ret=False):
        u"""Encuentra las regiones de interes del esquema de marcadores."""
        extra = np.array((self.cfg.getint('walk', 'roiwidth'),
                          self.cfg.getint('walk', 'roiheigth')))

        markersxroi = self.sch['markersxroi']
        for r in sorted(markersxroi):
            ends = markersxroi[r]
            roimin = np.min(markers[ends[0]: ends[-1]+1], axis=0) - extra
            roimax = np.max(markers[ends[0]: ends[-1]+1], axis=0) + extra
            self._regions[int(r)].append(np.array((roimin, roimax)).flatten())

        if ret:
            return self._regions

    def intp_regions(self, incp_indexes, full_indexes, regions, ret=False):
        """Crea las regiones de interes de los cuadros incompletos"""
        markersxroi = self.sch['markersxroi']
        for r in sorted(markersxroi):
            # Interpola por componentes (x1, y1, x2, y2)*full_indexes
            data = np.array(regions[int(r)]).transpose()
            intp = self.interpolate(incp_indexes, full_indexes, data)
            self._iregions[int(r)].append(intp.transpose())

        if ret:
            return self._iregions





##############################################################################
from configparser import ConfigParser
import unittest

stringcf = """
[walk]
roiwidth = 10
roiheigth = 10
"""

config = ConfigParser()
config.read_string(stringcf)

schema = {
"markersxroi": {'0':(0, 1), '1': (2, 3), '2': (4, 5, 6)}
}

class WalkTest(unittest.TestCase):
    w = Walk(config, schema)

    def test_interpolate(self):
        # Valores de una funcion en el plano cualquiera.
        XX = np.linspace(-np.pi, np.pi, 100)
        YY = np.vstack((np.sin(XX), np.cos(XX)))

        XP = np.linspace(-np.pi, np.pi, 15) # puntos en el dominio de la func.
        Y = np.vstack((np.sin(XP), np.cos(XP))) # valores esperados

        interp = self.w.interpolate(XP, XX, YY) # resultado de la interp.
        assert(np.all(np.round(Y, 2) == np.round(interp, 2)))

    def test_calcrois(self):
        markers = np.array((
            (100, 100),
            (120, 140),
            (300, 400),
            (300, 430),
            (130, 600),
            (125, 620),
            (160, 640)))
        result = self.w.calc_regions(markers, True)
        assert(np.all(result[0] == np.array((90, 90, 130, 150))))
        assert(np.all(result[1] == np.array((290, 390, 310, 440))))
        assert(np.all(result[2] == np.array((115, 590, 170, 650))))

    def test_intprois(self):
        full = (0, 2)
        incp = (1, )
        regions = {
            0: [np.array((1, 1, 2, 2)), np.array((3, 3, 4, 4))],
            1: [],
            2: []
        }
        result = self.w.intp_regions(incp, full, regions, True)
        assert(np.all(result[0] == np.array((2, 2, 3, 3))))

if __name__ == '__main__':
    unittest.main()
