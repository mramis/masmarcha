#!/usr/bin/env python
# coding: utf-8

'''Docstring
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


import numpy as np
import matplotlib.pyplot as plt

from markers import markerscollections

X00 = np.arange(-30, -20, 0.5)
X0 = np.arange(-20, -15, 0.5)
X1 = np.arange(-15, -10, 0.5)
X2 = np.arange(-10, -5, 0.5)
X3 = np.arange(-5, 0, 0.5)
X4 = np.arange(0, 10, 0.5)
X5 = np.arange(10, 15, 0.5)
X6 = np.arange(15, 25, 0.5)

F_X00 = np.zeros(X00.size)
F_X0 = np.sin(X0)*10
F_X1 = np.ones(X1.size) * -1
F_X2 = np.cos(X2)*10
F_X3 = np.zeros(X3.size)
F_X4 = np.square(X4)
F_X5 = np.zeros(X5.size)
F_X6 = X6 * -3

function = np.vstack((
    np.stack((F_X00, F_X00)).T,
    np.stack((X0, F_X0)).T,
    np.stack((F_X1, F_X1)).T,
    np.stack((X2, F_X2)).T,
    np.stack((F_X3, F_X3)).T,
    np.stack((X4, F_X4)).T,
    np.stack((F_X5, F_X5)).T,
    np.stack((X6, F_X6)).T
    ))

m = markerscollections()

for item in function:
    m.introduce(item)

b = m.interpolate()

print len(m) == len(b)
print m.stats()
print b.stats()

Xm = [item[0] for item in m]
Ym = [item[1] for item in m]
Xb = [item[0] for item in b]
Yb = [item[1] for item in b]

plt.plot(Xm, Ym, 'bo', color='greenyellow', markersize=12)
plt.plot(Xb, Yb, '3', color='red', markersize=8)
plt.show()
