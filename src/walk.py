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

schema = {
"n": 7,
"r": 3,
"markersxroi": ((0, 1), (2, 3), (4, 5, 6))}

class Walk(object):
    maxsize = 300

    def __init__(self, wid, config, schema):
        self.wid = wid
        self.cfg = config
        self.sch = schema
        self._cols = (1, 1, schema['n']*2, schema['r']*4, schema['r'])
        self._array = np.zeros((self.maxsize, sum(self._cols)), dtype=np.int16)
        self._currow = 0
        self._incompleted = []

    def __repr__(self):
        return 'W{0}'.format(self.wid)

    @property  # NUEVO
    def arrnrows(self):
        return np.arange(self._array.shape[0])

    @property  # NUEVO
    def arrpos(self):
        return self._array[:, 0]

    @property  # NUEVO
    def arrcompleted(self):
        return self._array[:, 1]

    @property  # NUEVO
    def ixmarkers(self):
        r0, r1, r2 = self.sch['markersxroi']
        imks = np.arange(self.sch['n']) * 2 + sum(self._cols[:2])
        return imks[r0,], imks[r1,], imks[r2,]

    @property  #NUEVO
    def iymarkers(self):
        r0, r1, r2 = self.sch['markersxroi']
        imks = np.arange(self.sch['n']) * 2 + sum(self._cols[:2]) + 1
        return imks[r0,], imks[r1,], imks[r2,]

    @property  # NUEVO
    def ixregion(self):
        r0 = np.arange(2) * 2 + sum(self._cols[:3])
        r1 = np.arange(2) * 2 + sum(self._cols[:3]) + 4
        r2 = np.arange(2) * 2 + sum(self._cols[:3]) + 8
        return r0, r1, r2

    @property  # NUEVO
    def iyregion(self):
        r0 = np.arange(2) * 2 + sum(self._cols[:3]) + 1
        r1 = np.arange(2) * 2 + sum(self._cols[:3]) + 5
        r2 = np.arange(2) * 2 + sum(self._cols[:3]) + 9
        return r0, r1, r2

    @property  # NUEVO
    def arrincompleted(self):
        return self._array[:, np.arange(self.sch['r']) + sum(self._cols[:4])]

    # @property
    # def markers(self):
    #     if self._array is not None:
    #         return self._array[:, 2: 16].reshape(self.length, 7, 2) # HARDCORE
    #
    # @property
    # def regions(self):
    #     if self._array is not None:
    #         return self._array[:, 16: 28].reshape(self.length, 3, 2, 2) #HARDCORE
    #
    # @property
    # def value_state(self):
    #     if self._array is not None:
    #         return self._array[:, 28:].reshape(self.length, 3)

    def append_centers(self, pos, fullschema, centers):  # NUEVO
        u"""Agrega información del cuadro de video."""
        if fullschema:
            data = np.hstack((pos, fullschema, centers.flatten()))
            self._array[self._currow, np.arange(sum(self._cols[:3]))] = data
        else:
            self._incompleted.append(centers)
        self._currow += 1

    def append_stop(self):  # NUEVO
        u"""Cierra la información de cuadros en la caminata."""
        lastcompleted = self.arrnrows[np.bool8(self.arrcompleted)][-1]
        self._array = self._array[:lastcompleted+1]

    def calculate_regions(self):  # NUEVO
        u"""Encuentra las regiones de interes del esquema de marcadores."""
        xextra = self.cfg.getint('walk', 'roiwidth')
        yextra = self.cfg.getint('walk', 'roiheigth')
        for x, rx in zip(w.ixmarkers, w.ixregion):
            _min = np.min(self._array[:, x], 1) - xextra
            _max = np.max(self._array[:, x], 1) + xextra
            self._array[:, rx] = np.vstack((_min, _max)).transpose()
        for y, ry in zip(w.iymarkers, w.iyregion):
            _min = np.min(self._array[:, y], 1) - yextra
            _max = np.max(self._array[:, y], 1) + yextra
            self._array[:, ry] = np.vstack((_min, _max)).transpose()

    def interpolate_regions(self):  # NUEVO
        u"""Crea las regiones de interes de los cuadros incompletos"""
        comp = self.arrnrows[np.bool8(self.arrcompleted)]
        inco = self.arrnrows[np.logical_not(np.bool8(self.arrcompleted))]
        regions = np.hstack(self.ixregion), np.hstack(self.iyregion)
        for r in np.hstack(regions):
            self._array[inco, r] = np.interp(inco, comp, self._array[comp, r])


### CONTINUAR ACA
    def detect_incompleted(self, index, markers):
        u"""Detecta los marcadores incompletos que pertenecen a cada región."""
        rois = self._array[index, np.arange(*self._index['roi'])]
        incr = int(rois.size / len(self.sch['markersxroi']))
        X, Y = np.arange(0, markers.size, 2), np.arange(1, markers.size, 2)
        new_markers = np.zeros(self.sch['n']*2, dtype=np.int16)

        for r, ends in sorted(self.sch['markersxroi'].items()):
            a, b = int(r) * incr, (int(r) + 1) * incr
            xmin, ymin, xmax, ymax = rois[np.arange(a, b)]
            xbool = np.logical_and(markers[X] > xmin, markers[X] < xmax)
            ybool = np.logical_and(markers[Y] > ymin, markers[Y] < ymax)
            markersbool = np.logical_and(xbool, ybool)
            if np.count_nonzero(markersbool) == len(ends):
                ix = np.array(ends) * 2
                iy = np.array(ends) * 2 + 1
                new_markers[ix] = markers[X[markersbool]]
                new_markers[iy] = markers[Y[markersbool]]
            else:
                self._array[index, self._index['inr'][0] + int(r)] = 1
        return new_markers

    def sort_foot(self):
        u"""ordena los marcadores de pie."""
        indexes = np.array(self.sch['markersxroi']['2'])
        # El 2 es por las dos primeras columnas del arreglo
        x = 2 + indexes * 2
        y = 2 + indexes * 2 + 1

        indexes = np.array((x, y)).transpose()
        ia, ib, ic = indexes
        ma, mb, mc = [self._array[:, xy] for xy in indexes]

        segments = np.array((ma-mb, mb-mc, mc-ma))
        sequence = np.array(((ia, ib), (ib, ic), (ic, ia)))
        distances = np.linalg.norm(segments, axis=2).transpose()

        ordered_distances = np.argsort(distances)
        ordered_indexes = []
        for row in sequence[ordered_distances]:
            A, B, C = row
            ia = np.intersect1d(A, C)
            ib = np.intersect1d(A, B)
            ic = np.intersect1d(B, C)
            ordered_indexes.append(np.hstack((ia, ib, ic)))
        for r, ix in enumerate(ordered_indexes):
            self._array[r, indexes.flatten()] = self._array[r, ix]

    def recovery(self):
        self.intp_regions()
        mkscolumns = np.arange(*self._index['mks'])
        for i, inco_markers in self._inco:
            self._array[i, mkscolumns] = self.detect_unfulled(i, inco_markers)
        self.sort_foot()

    def intp_markers(self):
        comp = self._array[self._full, self._index['inx'][0]]
        for r, group in self.sch['markersxroi'].items():
            inco = self._array[np.bool8(self.value_state.transpose()[int(r)]), 0]
            ix = 2 + np.array(group) * 2
            iy = 2 + np.array(group) * 2 + 1
            for m in np.hstack((ix, iy)):
                self._array[inco, m] = np.interp(inco, comp, self._array[comp, m])

    def get_markers(self):
        self.classify()
        self.recovery()
        self.intp_markers()
        return self.markers

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
        arr = np.ndarray(14)
        walk.append_centers(True, arr)
        assert(walk.data[0][1] is arr)

    def test_stop(self):
        walk = Walk(0, config, schema)
        arr = np.ndarray(14)
        for i in range(10):
            walk.append_centers(True, arr)
        for i in range(5):
            walk.append_centers(False, arr)
        walk.stop_walking(15)
        self.assertEqual(walk.lastpos, 10, 'message')

    def test_classify(self):
        walk = Walk(0, config, schema)
        arrt = np.arange(14)
        arrf = np.arange(16)
        walk.append_centers(True, arrt)
        walk.append_centers(False, arrf)
        walk.classify()
        assert(walk._array.shape[0] == 2)
        assert(walk._inco[0][1] is arrf)

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
        walk.append_centers(True, arr0)
        walk.append_centers(True, arr1)
        walk.append_centers(False, arr2)
        walk.append_centers(True, arr3)
        walk.classify()
        walk.intp_regions()
        result = walk._array[2, np.arange(*walk._index['roi'])]
        expected = np.array([-10, -9, 12, 13, -6, -5, 16, 17, -2, -1, 22, 23])
        assert(np.all(result == expected))

    def test_detectun(self):
        walk = Walk(0, config, schema)
        arr0 = np.array((
            (1059, 1743),
            (1071, 1770),
            (1085, 1830),
            (1081, 1850),
            (1062, 1940),
            (1061, 1955),
            (1091, 1955)))
        walk.append_centers(True, arr0.flatten())
        walk.classify()
        arr4 = arr0[4:].flatten()
        walk.detect_unfulled(0, arr4.flatten())

    def test_sortfoot(self):
        walk = Walk(0, config, schema)
        arr0 = np.array((
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (17, 60),
            (135, 60)))
        arr1 = np.array((
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (-6, 25),
            (141, 35),
            (30, 75)))
        walk.append_centers(True, arr0.flatten())
        walk.append_centers(True, arr1.flatten())
        walk.append_centers(True, arr0.flatten())
        walk.classify()
        walk.sort_foot()
        arr1 = np.array((
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (-6, 25),
            (30, 75),
            (141, 35)))
        assert(np.all(walk._array[1, np.arange(2, 16)] == arr1.flatten()))

    def test_recovery(self):
        walk = Walk(0, config, schema)
        arr0 = np.array((
            (1059, 1743),
            (1071, 1770),
            (1085, 1830),
            (1081, 1850),
            (1062, 1940),
            (1061, 1955),
            (1091, 1955)))
        arr1 = arr0[4:].flatten()
        arr2 = arr0 + np.array((5, 0))
        walk.append_centers(True, arr0.flatten())
        walk.append_centers(False, arr1.flatten())
        walk.append_centers(True, arr2.flatten())
        walk.classify()
        walk.recovery()

    def test_intpmks(self):
        walk = Walk(0, config, schema)
        arr0 = np.array((
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (17, 60),
            (135, 60)))
        arr1 = np.array((
            (0, 0),
            (0, 0),
            (0, 0),
            (0, 0),
            (-6, 25),
            (141, 35),
            (30, 75)))
        walk.append_centers(True, arr0.flatten())
        walk.append_centers(False, arr0.flatten())
        walk.append_centers(True, arr1.flatten())
        walk.classify()
        walk.recovery()
        walk.intp_markers()

        mks = walk._array[:, np.arange(10, 16)]
        for i in range(3):
            x, y = mks[i].reshape(3, 2).T
            plt.plot(x, -y)
        plt.show()
if __name__ == '__main__':
    unittest.main()
