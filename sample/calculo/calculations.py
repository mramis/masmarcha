#!usr/bin/env python
# coding: utf-8

'''Calculate the angle between two vectors, the direction of movement,
and a little of statics
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

def Angle(A, B):
    if type(A) is np.ndarray and type(B) is np.ndarray:
        normA = np.sqrt((A.dot(A.T).diagonal()))
        normB = np.sqrt((B.dot(B.T).diagonal()))
        pInternoAB = A.dot(B.T).diagonal()
        radiansAngle = np.arccos(pInternoAB / (normA * normB))
    else:
        raise Exception('A&B must be numpy arrays')
    return np.degrees(radiansAngle)

def Direction(MasterArray):
    '''Esta función asume que cada matriz de MasterArray contiene
    tres elementos: tiempo, x, y
    '''
    if type(MasterArray) is np.ndarray:
        rows, columns = MasterArray.shape[0], 1
        Xdirection = np.ndarray((rows, columns))
        for index, array in enumerate(MasterArray):
            firstRow, lastRow = array[0], array[-1]
            Xdirection[index] = (lastRow - firstRow)[1]
        average = np.average(Xdirection)
        if average > 0:
            directionValue = 1
        elif average < 0:
            directionValue = -1
        else:
            raise Exception('Direction value was not found')
    else:
        raise Exception('MasterArray must be numpy array')
    return directionValue

def polynomialRegression(master, degree):
    out = []
    for A in master:
        coeff, residual, __, __, __ = np.polyfit(
                np.arange(A.size),
                A,
                degree,
                full=True
        )
        polynomial = np.polyval(coeff, np.arange(A.size))
        St = np.square(A - A.mean()).sum()
        R2 = 1 - residual/St
        out.append([polynomial, R2])
    return(out)



