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

    @property
    def imarkers(self):
        array = []
        for x, y in zip(self.ixmarkers, self.iymarkers):
            array.append(np.vstack((x, y)).transpose().flatten())
        return array

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

    @property
    def iincompleted(self):  # nuevo
        return np.arange(self.sch['r']) + sum(self._cols[:4])

    @property  # NUEVO
    def arrincompleted(self):
        return self._array[:, self.iincompleted]

    def append_centers(self, pos, fullschema, centers):  # NUEVO
        u"""Agrega información del cuadro de video."""
        if fullschema:
            data = np.hstack((pos, fullschema, centers.flatten()))
            self._array[self._currow, np.arange(sum(self._cols[:3]))] = data
        else:
            data = (pos, fullschema)
            self._incompleted.append(centers)
            self._array[self._currow, np.arange(sum(self._cols[:2]))] = data
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

    def recover_incompleted(self):  # NUEVO
        incompleted = []
        axis = self.arrnrows[np.logical_not(self.arrcompleted)]
        for pos, centers in zip(axis, self._incompleted):
            xm = centers[:, 0]
            ym = centers[:, 1]
            for r, (ix, iy) in enumerate(zip(self.ixregion, self.iyregion)):
                x0, x1 = self._array[pos, ix]
                x = np.logical_and(xm > x0, xm < x1)
                y0, y1 = self._array[pos, iy]
                y = np.logical_and(ym > y0, ym < y1)
                substitution = centers[np.logical_and(x, y)]
                if len(substitution) == len(self.sch['markersxroi'][r]):
                    self._array[pos, self.imarkers[r]] = substitution.flatten()
                    incompleted.append(0)
                else:
                    incompleted.append(1)
            self._array[pos, self.iincompleted] = incompleted
            incompleted.clear()


#### DESDE ACA...
    def sort_foot(self):
        u"""ordena los marcadores de pie."""
        indexes = np.array(self.sch['markersxroi'][2])
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

#### HASTA ACA
    def interpolate_markers(self):  # NUEVO
        comp = self.arrnrows[np.bool8(self.arrcompleted)]
        for r, (mx, my) in enumerate(zip(self.ixmarkers, self.iymarkers)):
            inco = self.arrnrows[np.bool8(self.arrincompleted[:, r])]
            for m in np.hstack((mx, my)):
                interp = np.interp(inco, comp, self._array[comp, m])
                self._array[inco, m] = interp
