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


class Walk(object):
    __counter = 0
    maxsize = 2500

    def __init__(self, config):
        Walk.__counter += 1
        self.id = Walk.__counter
        self.config = config
        mplaces = config.getint('schema', 'n')
        rplaces = config.getint('schema', 'r')
        self._cols = (1, 1, mplaces*2, rplaces*4, rplaces)
        self._array = np.zeros((self.maxsize, sum(self._cols)), dtype=np.int16)
        self._currow = 0
        self._incompleted = []
        print("NewWalk %s" % self)

    def __repr__(self):
        return 'W{0}'.format(self.id)

    @classmethod
    def num_of_walks(cls):
        return cls.__counter

    @property
    def arrnrows(self):
        return np.arange(self._array.shape[0])

    @property
    def info(self):
        return (self.id, self._array[0, 0], self._array[-1, 0])

    @property
    def arrcompleted(self):
        return self._array[:, 1]

    @property
    def markersxroi(self):
        out = []
        stringtuple = self.config.get('schema', 'markersxroi')
        for tup in stringtuple.split('/'):
            stringvector = tup.split(',')
            out.append([int(x) for x in stringvector])
        return(out)

    @property
    def ixmarkers(self):
        r0, r1, r2 = self.markersxroi
        nmarkers = self.config.getint('schema', 'n')
        imks = np.arange(nmarkers) * 2 + sum(self._cols[:2])
        return imks[r0,], imks[r1,], imks[r2,]

    @property
    def iymarkers(self):
        r0, r1, r2 = self.markersxroi
        nmarkers = self.config.getint('schema', 'n')
        imks = np.arange(nmarkers) * 2 + sum(self._cols[:2]) + 1
        return imks[r0,], imks[r1,], imks[r2,]

    @property
    def imarkers(self):
        array = []
        for x, y in zip(self.ixmarkers, self.iymarkers):
            array.append(np.vstack((x, y)).transpose().flatten())
        return array

    @property

    def ixregion(self):
        r0 = np.arange(2) * 2 + sum(self._cols[:3])
        r1 = np.arange(2) * 2 + sum(self._cols[:3]) + 4
        r2 = np.arange(2) * 2 + sum(self._cols[:3]) + 8
        return r0, r1, r2

    @property

    def iyregion(self):
        r0 = np.arange(2) * 2 + sum(self._cols[:3]) + 1
        r1 = np.arange(2) * 2 + sum(self._cols[:3]) + 5
        r2 = np.arange(2) * 2 + sum(self._cols[:3]) + 9
        return r0, r1, r2

    @property
    def iincompleted(self):
        return np.arange(self.config.getint('schema','r')) + sum(self._cols[:4])

    @property
    def arrincompleted(self):
        return self._array[:, self.iincompleted]

    @property
    def regions(self):
        cols = np.arange(self._cols[3]) + sum(self._cols[:3])
        return self._array[:, cols].reshape(self._array.shape[0], 3, 2, 2)

    @property
    def markers(self):
        cols = np.arange(self._cols[2]) + sum(self._cols[:2])
        return self._array[:, cols]

    def append_centers(self, pos, fullschema, centers):
        u"""Agrega información del cuadro de video."""
        if fullschema:
            data = np.hstack((pos, fullschema, centers.flatten()))
            self._array[self._currow, np.arange(sum(self._cols[:3]))] = data
        else:
            data = (pos, fullschema)
            self._incompleted.append(centers)
            self._array[self._currow, np.arange(sum(self._cols[:2]))] = data
        self._currow += 1

    def append_stop(self):
        u"""Cierra la información de cuadros en la caminata."""
        lastcompleted = self.arrnrows[np.bool8(self.arrcompleted)][-1]
        self._array = self._array[:lastcompleted+1]
        print("EndWalk %s" % self)

    def calculate_regions(self):
        u"""Encuentra las regiones de interes del esquema de marcadores."""
        xextra = self.config.getint('walk', 'roiwidth')
        yextra = self.config.getint('walk', 'roiheight')
        for x, rx in zip(self.ixmarkers, self.ixregion):
            _min = np.min(self._array[:, x], 1) - xextra
            _max = np.max(self._array[:, x], 1) + xextra
            self._array[:, rx] = np.vstack((_min, _max)).transpose()
        for y, ry in zip(self.iymarkers, self.iyregion):
            _min = np.min(self._array[:, y], 1) - yextra
            _max = np.max(self._array[:, y], 1) + yextra
            self._array[:, ry] = np.vstack((_min, _max)).transpose()

    def interpolate_regions(self):
        u"""Crea las regiones de interes de los cuadros incompletos"""
        comp = self.arrnrows[np.bool8(self.arrcompleted)]
        inco = self.arrnrows[np.logical_not(np.bool8(self.arrcompleted))]
        regions = np.hstack(self.ixregion), np.hstack(self.iyregion)
        for r in np.hstack(regions):
            self._array[inco, r] = np.interp(inco, comp, self._array[comp, r])

    def recover_incompleted(self):
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
                if len(substitution) == len(self.markersxroi[r]):
                    self._array[pos, self.imarkers[r]] = substitution.flatten()
                    incompleted.append(0)
                else:
                    incompleted.append(1)
            self._array[pos, self.iincompleted] = incompleted
            incompleted.clear()

    def sort_foot(self):
        u"""ordena los marcadores de pie."""
        indexes = np.array(self.markersxroi[2])
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

    def interpolate_markers(self):
        for r, (mx, my) in enumerate(zip(self.ixmarkers, self.iymarkers)):
            indexes = np.bool8(self.arrincompleted[:, r])
            comp = self.arrnrows[np.logical_not(indexes)]
            inco = self.arrnrows[indexes]
            for m in np.hstack((mx, my)):
                interp = np.interp(inco, comp, self._array[comp, m])
                self._array[inco, m] = interp

    @property
    def direction(self):
        sm = int(self.config.get('schema', 'foot').split(',')[0])
        rf, ff = self.markers[:, (sm*2, (sm + 1) * 2)].transpose()
        return int((ff - rf).mean(axis=0) > 0)

    @property
    def dir(self):
        return self.direction

    def find_markers(self):
        self.calculate_regions()
        self.interpolate_regions()
        self.recover_incompleted()
        self.sort_foot()
        self.interpolate_markers()


if __name__ == '__main__':
    from settings import app_config
    walks = Walk(app_config)
