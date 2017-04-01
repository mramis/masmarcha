#!usr/bin/env python
# coding: utf-8

'''This module was create for manipulate the domain of joint-angles-data
and compare more than only-one text imput file.
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


from __future__ import division

import numpy as np

def linear(X, A0, A1):
    '''Define f_linear(x) = y, from y - y1 = m(x - x1) were
            m = y1 - y0 / x1 - x0
    Args:
        x: the x value to interpolate in the linear function f(x) = y;
        Pi: each one is 2-tuple with the (xi, yi) coordinate
            of two consecutive points in the plane.
    Returns:
        "numpy array (x, f(x) = y)" interpolated value.
    '''

    Ax, Ay = A0.T
    Bx, By = A1.T
    Y = (X - Ax).dot((By - Ay)/(Bx - Ax)) + Ay

    return np.hstack((X, Y)).reshape(*A0.shape).T


def linear_interpolation_range(A0, A1, steps):
    '''Interpola los datos que faltan en una cantidad finita de puntos dentro
    de un intervalo

    '''
    X0, X1 = A0[:, 0], A1[:, 0]
    DX = (X1 - X0)/(steps + 1)
    points = (X0 + X*DX for X in range(1, steps + 1))
    for p in points:
        yield linear(p, A0, A1)

if __name__ == '__main__':
    A = np.array((1,3,4,5,6,7)).reshape(3,2)
    B = np.array((5,4,2,1,3,4)).reshape(3,2)
    I = linear_interpolation_range(A, B, 1)
    print A
    print I.next()
    print B
