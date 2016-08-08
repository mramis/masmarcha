#!/usr/bin/env python
# coding: utf-8

'''regiones de interes en el cuadro de  video.
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

def roi(frame, equals=2, **kwargs):
    '''Generador. Divide el cuadro que se le pasa como argumento en partes
    iguales(filas) si ``equals != False``(por defecto 2). Si se quiere puede
    pasarse valores particulares, haciendo equals = False, y usando argumentos
    con nombre, e.g:
            >>> A = np.arange(24).reshape(6, 4)
            >>> roigen = split_into_roi(A,equals=False,lsup=(0,3),linf=(3,5))
            >>> upp_roi, low_roi = list(roigen)
    '''
    if equals:
        limit = frame.shape[0]/equals
        start = 0
        end = limit
        for roi in xrange(equals):
            yield frame[start:end, :]
            start = end
            end += limit
    else:
        for sup_l, inf_l in sorted(kwargs.values()):
            yield frame[sup_l:inf_l, :]
