#!/usr/bin/env python
# coding: utf-8

"""Módulo de cálculo para operaciones de video.
El código esta escrito en Cython.
"""

# Copyright (C) 2017  Mariano Ramis

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


def centroid(int x, int y, int w, int h):
    u"""Calula el centro de una caja.

    :param x, y: Vértice superior izquierdo.
    :param w, h: Ancho y Alto de la caja.
    """
    cdef int xc = x + w/2
    cdef int yc = y + h/2
    return xc, yc
