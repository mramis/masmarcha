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
from scipy import ndimage


NEIGHBORS = ndimage.generate_binary_structure(2, 2)


def classifier(frame, n, groupby=NotImplemented):
    '''
    Args:
            frames: arreglo binario de pixeles.
            n: número de markadores que se está buscando.
            groupby: tuple que nos informa sobre la forma de agrupar estos
            datos.
    Returns:
            arreglo 2D de centros de masa (y, x) de los marcadores si se
            encontró el número correcto, de otra manera, retorna un arreglo
            de ceros de la misma dimension.
    '''
    labeled_frame, n_finded = ndimage.label(frame, NEIGHBORS)
    if n_finded == n:
        COM = ndimage.center_of_mass(frame, labeled_frame, np.arange(1, n + 1))
        return np.array(COM)
    elif n_finded == 0:
        false = np.ndarray((n, 2))
        false.fill(-1)
        return false
    else:
        return np.zeros((n, 2))
