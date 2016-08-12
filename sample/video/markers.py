#!/usr/bin/env python
# coding: utf-8

'''
'''

# Copyright (C) 2016  Mariano Ramis

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


from __future__ import division
from collections import deque
import cPickle

import numpy as np


class markerscollections(object):

    def __init__(self, data=None):
        if not data:
            self._deque = deque(maxlen=3000)
        else:
            self._deque = deque(data)
        self._frames = 0
        self._lostframes = 0
        self._overloadframes = 0
        self._jump = 0

    def __repr__(self):
        return self._deque.__repr__()

    def introduce(self, element):
        if element is None:
            self._jump += 1
            self._lostframes += 1
            if self._jump == 5:
                self.clearlastn()
                self._deque.append('JUMPING FRAME')
                return
            if self._jump > 5:
                return
            self._deque.append(element)
        else:
            self._jump = 0
            self._frames += 1
            self._deque.append(element)

    def clearlastn(self, n=4):
        for __ in xrange(n):
            self._deque.pop()

    def stats(self):
        ttframes = self._frames + self._lostframes + self._overloadframes
        relative_f = self._frames / ttframes * 100
        relative_lf = self._lostframes / ttframes * 100
        relative_olf = self._overloadframes / ttframes * 100
        return {'SuccessFrames': '{:2.2f}%'.format(relative_f),
                'LoosesFrames': '{:2.2f}%'.format(relative_lf),
                'Overloadframes': '{:2.2f}%'.format(relative_olf)}

    def dump(self, filename='sample.txt'):
        stats = {'-f': self._frames,
                 '-lf': self._lostframes,
                 '-olf': self._overloadframes}
        with open(filename, 'w') as filehandler:
            cPickle.dump((self._deque, stats), filehandler)

    def load(self, filename='sample.txt'):
        with open(filename) as filehandler:
            data = cPickle.load(filehandler)
            self._deque = data[0]
            self._frames = data[1]['-f']
            self._lostframes = data[1]['-lf']
            self._overloadframes = data[1]['-olf']
