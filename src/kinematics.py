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


class Kinematics(object):

    def __init__(self, config):
        self.config = config
        self.fps = config.getint('camera', 'fps')
        self.stpsize = config.getint('kinematics', 'stpsize')
        self.maxcycles = config.getint('kinematics', 'maxcycles')
        self.anglessize = config.getint('kinematics', 'anglessize')
        self.columns = ((1, self.stpsize,) + (self.anglessize,) * 3)

    def start(self):
        self._array = np.ndarray((self.maxcycles, sum(self.columns)))
        self._cyclesid = []
        self._motion = []
        self._counter = 0

    @property
    def sptindex(self):
        start = sum(self.columns[:1])
        return np.arange(start, start + self.stpsize)

    @property
    def hipindex(self):
        start = sum(self.columns[:2])
        return np.arange(start, start + self.anglessize)

    @property
    def kneeindex(self):
        start = sum(self.columns[:3])
        return np.arange(start, start + self.anglessize)

    @property
    def ankleindex(self):
        start = sum(self.columns[:4])
        return np.arange(start, start + self.anglessize)

    @property
    def legdistances(self):
        ldis = self.config.getfloat('kinematics', 'llength')
        rdis = self.config.getfloat('kinematics', 'rlength')
        return (ldis, rdis)

    @property
    def stridemarker(self):
        return int(self.config.get('schema', 'foot').split(',')[0])

    @property
    def segments(self):
        return self.config.get('schema', 'order_segments').split(',')

    @property
    def cyclemarkers(self):
        cm1 = int(self.config.get('kinematics', 'cyclemarker1').split('M')[1])
        cm2 = int(self.config.get('kinematics', 'cyclemarker2').split('M')[1])
        return np.array(((cm1*2, cm1*2 +1), (cm2*2, cm2*2 +1)))

    def build_segments(self, markers):
        ix = np.arange(self.config.getint('schema', 'n')) * 2
        iy = ix + 1
        indexes = np.array((ix, iy)).transpose()

        segments = []
        for s in self.segments:
            a, b = [int(m) for m in self.config.get('schema', s).split(',')]
            segments.append(markers[:, indexes[b]] - markers[:, indexes[a]])
        return segments

    def cycler(self, walk):
        # Se deriva la posicion de los marcadores de pie para obtener velocidad
        cm1, cm2 = self.cyclemarkers
        mks = walk.markers[:, cm1], walk.markers[:, cm2]
        diff = np.abs(np.gradient(mks, axis=1).mean(axis=2))
        self.soft_curve(diff[0])
        self.soft_curve(diff[1])

        # Se filtran las velocidades que son menores al umbral establecido.
        lth = self.config.getfloat('kinematics', 'lthreshold')
        rth = self.config.getfloat('kinematics', 'rthreshold')
        direction = self.walk_direction(walk)
        threshold = (lth, rth)[direction]
        mot = np.logical_and(*(diff >= threshold))

        self._motion.append(np.vstack((diff, mot)))

        # Se consiguen los ciclos dentro de la caminata según el pie cambie de
        # estar moviendose a apoyarse.
        strike = []
        for i, (previousf, nextf) in enumerate(zip(mot[:-1], mot[1:])):
            if previousf and not nextf:
                strike.append(i+1)
            if not previousf and nextf:
                toe_off = i+1
            if len(strike) == 2:
                cycle_id = "W%sC%d" % (walk.id, self._counter)
                cycle_def = strike[0], toe_off, strike[1]

                yield (cycle_id, direction, cycle_def)

                strike.pop(0)
                self._counter += 1

    def pixel_scale(self, markers, legdistance):
        a, b = [int(m) for m in self.config.get('schema', 'leg').split(',')]
        m0 = a * 2, a * 2 + 1
        m1 = b * 2, b * 2 + 1
        div = np.linalg.norm(markers[:, m0] - markers[:, m1], axis=1).mean()
        return(legdistance / div)

    def reshape(self, sample):
        u"""Modifica el tamaño de la muestra a n valores."""
        n = self.config.getint('kinematics', 'anglessize')
        rows, cols = sample.shape
        x = np.linspace(0, cols, n)
        xs = np.arange(cols)
        resized = np.empty((rows, n))
        for e, joint in enumerate(sample):
            resized[e] = np.interp(x, xs, joint)
        return resized.flatten()

    def soft_curve(self, curve, loops=10):
        for i in range(loops):
            pos = 1
            for pre, post in zip(curve[0:-2], curve[2:]):
                curve[pos] = np.mean((pre, post))
                pos += 1

    def walk_direction(self, walk):
        im = self.stridemarker
        rf, ff = walk.markers[:, (im*2, (im + 1) * 2)].transpose()
        return int((ff - rf).mean(axis=0) > 0)

    def calculate_params(self, walk):
        fps = self.fps
        stridem = self.stridemarker
        leglenght = self.legdistances
        CAngles = Angles()
        CSpatioTemp = SpatioTemporal()
        for cycleid, direction, definition in self.cycler(walk):
            ftstrike, toeoff, sdstrike = definition
            markers = walk.markers[ftstrike: sdstrike]
            scale = self.pixel_scale(markers, leglenght[direction])
            angles = CAngles.calculate(self.build_segments(markers), direction)
            spatiotemp = CSpatioTemp.calculate(markers, direction, definition,
                                               fps, scale, stridem)
            self._cyclesid.append(cycleid)
            self.join(direction, spatiotemp, self.reshape(angles))

    def join(self, *params):
        self._array[self._counter] = np.hstack(params)

    def close(self):
        self._array = self._array[:self._counter]

    def remove(self, toremove):
        u"""Remueve los datos correspondientes de los ciclos."""
        rm = []
        inx = np.arange(len(self._cyclesid), dtype=np.int16)
        for cid in toremove:
            if 'C' in cid:
                rm += inx[[c == cid for c in self._cyclesid]].tolist()
            else:
                rm += inx[[c.startswith(cid) for c in self._cyclesid]].tolist()
        for cid in np.array(self._cyclesid)[rm]:
            self._cyclesid.remove(cid)
        self._counter = len(self._cyclesid)
        self._array = np.delete(self._array, rm, axis=0)

    def to_plot(self):
        return (np.asarray(self._cyclesid, dtype='U8'),
                self._array[:, 0],
                self._array[:, self.sptindex],
                self._array[:, self.hipindex],
                self._array[:, self.kneeindex],
                self._array[:, self.ankleindex])


class SpatioTemporal(object):

    def spatial(self, marker, scale):
        u"""Calcula la longitud de la zacada."""
        return np.linalg.norm(marker[-1] - marker[0])*scale

    def temporal(self, fps, *cycle_def):
        u"""Calcula los parámetros temporales."""
        fts, tef, sds = cycle_def
        fduration = sds - fts
        sduration = float(fduration) / fps
        stance = (tef - fts) / fduration * 100
        swing = (sds - tef) / fduration * 100
        return (sduration, stance, swing)

    def velocity(self, duration, stride):
        u"""Calcula los parámetros de velocidad."""
        # cadency, velocity
        return (120 / duration, stride / duration)

    def calculate(self, markers, direction, cycledef, fps, scale, im):
        u"""Obtine los parámetros espaciotemporales del ciclo."""
        str = self.spatial(markers[:, (im*2, im*2+1)], scale)
        dur, sta, swi = self.temporal(fps, *cycledef)
        cad, vel = self.velocity(dur, str)
        return(dur, sta, swi, str, cad, vel)


class Angles(object):

    def angle(self, A, B):
        """Calcula el ángulo(theta) entre dos vectores."""
        NA = np.linalg.norm(A, axis=1)
        NB = np.linalg.norm(B, axis=1)
        AB = A.dot(B.T).diagonal()
        return np.degrees(np.arccos(AB / (NA * NB)))

    def canonicalX(self, nrows, sign):
        u"""arreglo de vectores unitarios."""
        array = np.zeros((nrows, 2))
        array[:, 0] = sign
        return array

    def hip_joint(self, tight, canonical):
        u"""Angulos de la articulación de cadera."""
        return 90 - self.angle(tight, canonical)

    def knee_joint(self, hip, leg, canonical):
        u"""Angulos de la articulación de rodilla."""
        return hip + self.angle(leg, canonical) - 90

    def ankle_joint(self, leg, foot):
        u"""Angulos de la articulación de tobillo."""
        return 90 - self.angle(leg * -1, foot)

    def calculate(self, segments, direction):
        nrows = segments[0].shape[0]
        canonical = self.canonicalX(nrows, (-1, 1)[direction])

        hip = self.hip_joint(segments[0], canonical)
        knee = self.knee_joint(hip, segments[1], canonical)
        ankle = self.ankle_joint(segments[1], segments[2])
        return np.array((hip, knee, ankle))
