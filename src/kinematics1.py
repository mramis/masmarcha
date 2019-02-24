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
        footvelocity = self.make_soft(np.diff(footmarkers, axis=1).mean(2))
        footmotion = np.logical_and(*(footvelocity >= lrthreshold[walk.dir]))
        for (c1, c2, c3) in self.cycler(footmotion):
            self.cyclessv[self.counter] = np.hstack(
                (self.counter, walk.id, walk.dir, (c1, c2, c3)))
            self.cyclesmk[self.counter] = self.resize(walk.markers[c1:c3, :])

    def make_soft(self, array, loops=10):
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
