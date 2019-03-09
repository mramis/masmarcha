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


import sys
import numpy as np


class Schema(object):
    """docstring for Schema."""
    def __init__(self, config):
        self.config = config

    def get_marker(self, markersarray, position):
        if len(markersarray.shape) == 2:
            return markersarray[:, (position * 2, position * 2 + 1)]
        elif len(markersarray.shape) == 3:
            return markersarray[:, :, (position * 2, position * 2 + 1)]

    def get_segment(self, markersarray, segment):
        a, b = [int(s) for s in self.config.get('schema', segment).split(',')]
        return (self.get_marker(markersarray, a) -
                self.get_marker(markersarray, b))


class Cycler(object):
    maxcycles = 50

    def __init__(self, config):
        u"""."""
        self.config = config
        self.start()

    def stop(self):
        self.cyclessv = self.cyclessv[:self.counter]
        self.cyclesmk = self.cyclesmk[:self.counter]

    def cycler(self, footmotion):
        u"""."""
        strike = []
        prevframe, nextframe = footmotion[:-1], footmotion[1:]
        for i, (prev, next) in enumerate(zip(prevframe, nextframe)):
            if prev and not next:
                strike.append(i+1)
            if not prev and next:
                toe_off = i+1
            if len(strike) == 2:
                yield (strike[0], toe_off, strike[1])
                self.counter += 1
                strike.pop(0)

    def find_cycles(self, walk, footindexes, lrthreshold):
        u"""."""
        rear, front = footindexes
        footmarkers = walk.markers[:, rear], walk.markers[:, front]
        footvelocity = self.soft(np.abs(np.diff(footmarkers, axis=1).mean(2)))

        footmotion = np.logical_and(*(footvelocity >= lrthreshold[walk.dir]))
        for (c1, c2, c3) in self.cycler(footmotion):
            self.cyclessv[self.counter] = np.hstack(
                (self.counter, walk.id, walk.dir, (c1, c2, c3)))
            self.cyclesmk[self.counter] = self.resize(walk.markers[c1:c3, :])

    def soft(self, array, loops=10):
        u"""."""
        for i in range(loops):
            pre = array[:-2, :]
            pos = array[2:, :]
            array[1:-1, :] = np.mean((pre, pos), axis=0)
        return array

    def resize(self, sample):
        nrows, ncols = sample.shape
        xarange = np.arange(nrows)
        newsample = np.ndarray((100, ncols))
        newdomain = np.linspace(0, nrows, 100)
        for c, values in enumerate(sample.transpose()):
            newsample[:, c] = np.interp(newdomain, xarange, values)
        return newsample

    def start(self):
        u"""."""
        nmarkers = self.config.getint('schema', 'n') * 2
        self.counter = 0
        self.cyclessv = np.ndarray((self.maxcycles, 6), dtype=np.int32)
        self.cyclesmk = np.ndarray((self.maxcycles, 100, nmarkers))


class Kinematics(object):

    def __init__(self, config):
        self.config = config
        self.start()

    def start(self):
        self.cycler = Cycler(self.config)
        self.angles = Angles()
        self.stp = SpatioTemporal(self.config)

    @property
    def cyclemarkers(self):
        cm1 = int(self.config.get('kinematics', 'cyclemarker1').split('M')[1])
        cm2 = int(self.config.get('kinematics', 'cyclemarker2').split('M')[1])
        return np.array(((cm1*2, cm1*2 +1), (cm2*2, cm2*2 +1)))

    @property
    def footvelocitythreshold(self):
        lth = self.config.getfloat('kinematics', 'leftthreshold')
        rth = self.config.getfloat('kinematics', 'rightthreshold')
        return (lth, rth)

    def cycle_walks(self, walks):
        cyclemarkers = self.cyclemarkers
        lrthreshold = self.footvelocitythreshold
        for walk in walks:
            self.cycler.find_cycles(walk, cyclemarkers, lrthreshold)
        self.cycler.stop()

    def build_segments(self):
        # NOTE: MODIFICAR CON LA CLASE SCHEMA
        ix = np.arange(self.config.getint('schema', 'n')) * 2
        iy = np.arange(self.config.getint('schema', 'n')) * 2 + 1
        indexes = np.array((ix, iy)).transpose()

        ncycles, ndata, nmarkers = self.cycler.cyclesmk.shape
        ordersegments = self.config.get('schema', 'order_segments').split(',')
        segments = np.ndarray((ncycles, ndata, len(ordersegments) * 2))
        mk = self.cycler.cyclesmk
        for i, s in enumerate(ordersegments):
            place = (i*2, i*2+1)
            a, b = [int(m) for m in self.config.get('schema', s).split(',')]
            segments[:, :, place] = mk[:, :, indexes[b]] - mk[:, :, indexes[a]]
        return segments

    def calculate_angles(self):
        direction = self.cycler.cyclessv[:, 2]
        segments = self.build_segments()
        return self.angles.calculate(segments, direction)

    def calculate_stp(self):
        rfmarker = self.cycler.cyclesmk[:, :, (10, 11)]
        legmarkers = self.cycler.cyclesmk[:, :, 6:10]
        return self.stp.calculate(self.cycler.cyclessv, self.cycler.cyclesmk)


class SpatioTemporal(object):

    def __init__(self, config):
        self.config = config
        self.schema = Schema(config)

    def _scale(self, markers, legdistance):
        """Calcula la escala entre pixeles y metros.

        Toma como referencia la distancia entre los marcadores de las piernas.
        :param markers: arreglo de marcadores de 3 dimensiones (nciclos,
         ndatos, 14coordenas).
        :type markers: numpy(3darray)
        :param legdistances: vector con las distancias de cada pierna segun la
         cantidad de ciclos (nciclos).
        :type legdistances: numpy.(1darray)
        :return: la escala para convertir la distacia de pixeles a metros.
        :rtype: numpy(1darray)
        """
        __, n, __ = markers.shape
        leg = self.schema.get_segment(markers, 'leg')
        realdistance = np.repeat(legdistance, n).reshape((legdistance.size), n)
        pixeldistance = np.linalg.norm(leg, axis=-1)
        return (realdistance / pixeldistance).mean(axis=-1)

    def _legdistance(self, direction):
        ldis = self.config.getfloat('kinematics', 'leftlength')
        rdis = self.config.getfloat('kinematics', 'rightlength')
        distances = np.ndarray((direction.size))
        distances[direction == 0] = ldis
        distances[direction == 1] = rdis
        return distances

    def stride(self, markers, scale):
        u"""Calcula la longitud de la zacada."""
        m5 = self.schema.get_marker(markers, 5)
        stridedistance = np.linalg.norm(m5[:, 0] - m5[:, -1], axis=1)
        return stridedistance * scale

    def temporal(self, fps, cyclessv):
        u"""Calcula los parámetros temporales."""
        fts, tef, sds = cyclessv[:, 3:].transpose()
        tcycle = (sds - fts) / fps
        tstance = (tef - fts) / fps
        tswing = tcycle - tstance
        return (tcycle, tstance, tswing,
                tstance / tcycle * 100, tswing / tcycle * 100)

    def velocity(self, duration, stride):
        u"""Calcula los parámetros de velocidad."""
        # cadency, velocity
        return (120 / duration, stride / duration)

    def calculate(self, cyclessv, cyclesmk):
        u"""Obtine los parámetros espaciotemporales del ciclo."""
        ncycles, __ = cyclessv.shape
        stp = np.ndarray((ncycles, 9))

        realdistances = self._legdistance(cyclessv[:, 2])
        pxtom = self._scale(cyclesmk, realdistances)
        stp[:, 6] = self.stride(cyclesmk, pxtom)

        fps = self.config.getint('camera', 'fps')
        correction = self.config.getint('camera', 'fpscorrection')

        stp[:, 1: 6] = np.array(self.temporal(fps*correction, cyclessv)).transpose()
        stp[:, 7:] = np.array(self.velocity(stp[:, 1], stp[:, 6])).transpose()
        return stp


class Angles(object):

    def angle(self, A, B):
        """Calcula el ángulo entre dos vectores."""
        ncycles, nrows, ncols = A.shape
        degrees = np.ndarray((ncycles, nrows))
        for i, (a, b) in enumerate(zip(A, B)):
            na = np.linalg.norm(A[i], axis=1)
            nb = np.linalg.norm(B[i], axis=1)
            ab = a.dot(b.transpose()).diagonal()
            degrees[i] = np.degrees(np.arccos(ab / (na * nb)))
        return degrees

    def canonicalX(self, direction):
        u"""arreglo de vectores unitarios."""
        sign = direction.copy().reshape(direction.size, 1)
        canonical = np.zeros((direction.size, 100, 2))
        sign[direction == 0] = -1
        canonical[:, :, 0] = sign
        return canonical

    def hip_joint(self, tight, canonical):
        u"""Angulos de la articulación de cadera."""
        return 90 - self.angle(tight, canonical)

    def knee_joint(self, tight, leg, canonical):
        u"""Angulos de la articulación de rodilla."""
        return self.angle(leg, canonical) - self.angle(tight, canonical)

    def ankle_joint(self, leg, foot):
        u"""Angulos de la articulación de tobillo."""
        return self.angle(leg, foot) - 90

    def calculate(self, segments, direction):
        canonical = self.canonicalX(direction)
        # NOTE: ESTO ESTA BASTANE MAL, TANTO LLAMAR A CONFIG PARA AHORA HACERLO HARDCORE
        hip = self.hip_joint(segments[:, :, (0, 1)], canonical)
        knee = self.knee_joint(segments[:, :, (0, 1)], segments[:, :, (2, 3)], canonical)
        ankle = self.ankle_joint(segments[:, :, (2, 3)], segments[:, :, (4, 5)])
        return np.array((hip, knee, ankle))
