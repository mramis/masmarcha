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

from frame import roi

neighbs = ndimage.generate_binary_structure(2,2)

def inspectframe(frame, n, mask=None, name=''):

# quizás esto no debe ir aquí
    labeled_frame, n_labels = ndimage.label(frame, structure=neighbs)

    if n_labels != n:
        print 'WARNING: [%s] número de marcadores incorrecto' % name



Orden:
verificar que el cuadro tenga la cantidad de elementos necesarios.
si no es así entonces se tiene que guardar esa información para interpolar.
que se encuentren el número correcto de marcadores, no significa que se
hayan encontrados los correctos, cómo se puede saltear este paso?
lo que se me ocurre que puede hacerse es establecer tres cuadros consecutivos
con los marcadores, e interpolarlos, si el punto interpolado está en un
entorno reducido, entonces los datos están bien!
---
se recibe el primer cuadro, no están todos los marcadores...
se recibe el segundo cuadro, no están todos los marcadores...
cuando se obtienen todos los datos, se setean las posiciones de los marcadores:w






