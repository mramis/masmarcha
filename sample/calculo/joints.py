#!usr/bin/env python
# coding: utf-8

'''Here's where it's definied joints angles.
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
from canonicalVectors import positiveY, negativeY
from calculations import Angle

def hipAngles(hipArrayPoints, kneeArrayPoints):
    HAP = hipArrayPoints
    KAP = kneeArrayPoints
    if type(HAP) != np.ndarray and type(KAP) != np.ndarray:
        raise ValueError('Arrays must be Numpy Arrays')
    thigh = KAP - HAP
    return Angle(negativeY, thigh)
