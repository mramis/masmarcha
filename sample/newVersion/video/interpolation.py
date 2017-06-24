# coding: utf-8

'''
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


def interpolate(Ai, Af, steps):
    '''
    '''
    # El spacio fila de los arreglos A corresponde a los marcadores. El espacio
    # columna a las cordenadas de esos marcadores
    Y0, X0 = Ai.T
    Y1, X1 = Af.T
    # conseguimos los x de los cuadros perdidos.
    steps = np.ones(X0.shape)*(steps + 2)
    gap = np.stack((X0, X1, steps))
    linspace = lambda A: np.linspace(A[0], A[1], A[2])
    X = np.apply_along_axis(linspace, 0, gap)[1:-1, :]
    print X
    # separamos los x de los y para la función np.interp
    xp = np.array((Ai[:, 1], Af[:, 1])).T
    fp = np.array((Ai[:, 0], Af[:, 0])).T
    interpolate = lambda A, B, X, i: np.interp(X.T[i], A[i], B[i])
    markers = []
    for i in xrange(Ai.shape[0]):
        markers.append(zip(X.T[i], interpolate(xp, fp, X, i)))
    print np.array(zip(markers[0], l[1]))

if __name__ == '__main__':
    AI = np.array(
        ((2, 4),  # cadera
         (8, 10))  # rodilla
        )
    AF = np.array(
        ((3, 5),  # cadera
         (8, 20))  # rodilla
        )
    interpolate(AI, AF, 4)
