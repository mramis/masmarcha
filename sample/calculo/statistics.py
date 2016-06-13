#!usr/bin/env python
# coding: utf-8

'''DOCSTRING
'''

# Copyright (C) 2016  Mariano Ramis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np

def linear(xi, P1, P2):
    x1, y1 = P1
    x2, y2 = P2
    yi = (y2 - y1)/(x2 - x1)*(xi - x1) + y1
    return np.array((xi, yi))

def interpolateRange(P1, P2, domain):
    _range =  np.unique(domain.clip(P1[0], P2[0]))[:-1]
    out = np.array(())
    for xi in _range:
        out = np.append(out, linear(xi, P1, P2))
    return out.reshape(out.size/2, 2)

def interpolateArray(array, domain):
    out = np.array(())
    P0 = array.T[0]
    for index, P1 in enumerate(array.T):
        if index is 0:
            continue
        out = np.append(out, interpolateRange(P0, P1, domain))
        P0 = P1
    out = np.append(out, P1)
    return out.reshape(out.size/2, 2)

def cycleEqualizer(Arrays):
    cycleArrays = np.array([np.arange(array.size) for array in Arrays])
    sizes = [(array.size - 1) for array in cycleArrays]
    _max = max(sizes)
    equalizedArrays = np.ndarray(Arrays.shape, dtype=object)
    common = np.array(())
    for index, element in enumerate(sizes):
        coeff = _max / float(element)
        equalized = cycleArrays[index] * coeff
        combined = np.stack((equalized, Arrays[index]))
        common = np.append(common, equalized)
        equalizedArrays[index] = combined
    return equalizedArrays, np.unique(common)  


if __name__ == '__main__':
    
    A = np.arange(15, dtype=float)
    B = np.arange(16, dtype=float)
    C = np.arange(17, dtype=float)
    D = np.arange(15, dtype=float)
    E = np.arange(14, dtype=float)



