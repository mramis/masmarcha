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


import numpy as np
import matplotlib.pyplot as plt


class Walk(object):

    def __init__(self, startpos, config, schema):
        self.cfg = config
        self.sch = schema
        self.data = []
        self._inco = []
        self._full = None
        self._array = None
        self._index = None
        self.startpos = startpos

    def __repr__(self):
        return 'W{0}'.format(self.id)

    def add_data(self, fullschema, centers):
        u"""Agrega información del cuadro de video."""
        self.data.append((fullschema, centers))

    def stop_walking(self, lastpos):
        u"""Cierra la información de cuadros en la caminata."""
        self.lastpos = lastpos
        while True:
            full = self.data[-1][0]
            if not full:
                self.data.pop()
                self.lastpos += -1
            else:
                break

    def classify(self):
        u"""Realiza la indentificación de los marcadores según el esquema."""
        nmark, nrois = self.sch['n'], len(self.sch['markersxroi'])
        ix = 1, 1, nmark*2, nrois*4, nrois
        nrows, ncols = len(self.data), sum(ix)

        self._array = np.zeros((nrows, ncols), dtype=np.int16)
        self._array[:, 0] = np.arange(nrows, dtype=np.int16)

        first, self._index = 0, {}
        for k, last in zip(("inx", "ful", "mks", "roi", "inr"), ix):
            self._index[k] = first, first + last
            first += last

        for i, (full, markers) in enumerate(self.data):
            if full:
                rois = self.calc_regions(markers)
                j, k = self._index['ful'][0], self._index['roi'][1]
                self._array[i, j:k] = np.hstack((1, markers, rois))
            else:
                self._inco.append(markers)

    def calc_regions(self, markers):
        u"""Encuentra las regiones de interes del esquema de marcadores."""
        extra = np.array((self.cfg.getint('walk', 'roiwidth'),
                          self.cfg.getint('walk', 'roiheigth')))
        rois = []
        for r, ends in sorted(self.sch['markersxroi'].items()):
            ix = np.array(ends) * 2
            iy = np.array(ends) * 2 + 1
            roimin = np.min((markers[ix], markers[iy]), axis=1) - extra
            roimax = np.max((markers[ix], markers[iy]), axis=1) + extra
            rois.append((roimin, roimax))
        return np.array(rois).flatten()

    def intp_regions(self):
        """Crea las regiones de interes de los cuadros incompletos"""
        self._full = np.bool8(self._array[:, self._index['ful'][0]])
        comp = self._array[self._full, self._index['inx'][0]]
        inco = self._array[np.logical_not(self._full), self._index['inx'][0]]
        for r in range(*self._index['roi']):
            self._array[inco, r] = np.interp(inco, comp, self._array[comp, r])

    def recovery(self):
        

    # def in_region(self, imarkers, iregion):
    #     u"""Devuelve los marcadores que pertenecen a la región."""
    #     r, (xmin, ymin, xmax, ymax) = iregion
    #     x = np.logical_and(imarkers[:, 0] > xmin, imarkers[:, 0] < xmax)
    #     y = np.logical_and(imarkers[:, 1] > ymin, imarkers[:, 1] < ymax)
    #     bmarkers = np.logical_and(x, y)
    #     n = len(self.sch['markersxroi'][r])
    #     if np.count_nonzero(bmarkers) == n:
    #         return True, imarkers[bmarkers]
    #     else:
    #         return False, np.zeros((n, 2))


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
"n": 7,
"markersxroi": {'0':(0, 1), '1': (2, 3), '2': (4, 5, 6)}
}

class WalkTest(unittest.TestCase):

    def test_adddata(self):
        walk = Walk(0, config, schema)
        arr = np.ndarray((7, 2))
        walk.add_data(True, arr)
        assert(walk.data[0][1] is arr)

    def test_stop(self):
        walk = Walk(0, config, schema)
        arr = np.ndarray((7, 2))
        for i in range(10):
            walk.add_data(True, arr)
        for i in range(5):
            walk.add_data(False, arr)
        walk.stop_walking(15)
        self.assertEqual(walk.lastpos, 10, 'message')

    def test_classify(self):
        walk = Walk(0, config, schema)
        arrt = np.arange(14)
        arrf = np.arange(16)
        walk.add_data(True, arrt)
        walk.add_data(False, arrf)
        walk.classify()
        assert(walk._array.shape[0] == 2)
        assert(walk._inco[0] is arrf)

    def test_calcrois(self):
        walk = Walk(0, config, schema)
        markers = np.arange(14)
        result = walk.calc_regions(markers)
        expected = np.array([-10, -9, 12, 13, -6, -5, 16, 17, -2, -1, 22, 23])
        assert(np.all(result == expected))

    def test_intprois(self):
        walk = Walk(0, config, schema)
        arr0 = np.arange(14)
        arr1 = np.arange(14)
        arr2 = np.arange(16)
        arr3 = np.arange(14)
        walk.add_data(True, arr0)
        walk.add_data(True, arr1)
        walk.add_data(False, arr2)
        walk.add_data(True, arr3)
        walk.classify()
        walk.intp_regions()
        result = walk._array[2, np.arange(*walk._index['roi'])]
        expected = np.array([-10, -9, 12, 13, -6, -5, 16, 17, -2, -1, 22, 23])
        assert(np.all(result == expected))


if __name__ == '__main__':
    unittest.main()
