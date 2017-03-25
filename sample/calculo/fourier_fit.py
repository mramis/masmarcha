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

def is_even(array):
    '''If len(array) is even return True, else return False.'''
    return array.size % 2 == 0


def fourierfit(array, sample=100, amplitud=4):
    '''Retorna una aproximación de fourier con espectro que se
    define en ``amplitud``. Por defecto la muestra es de 100
    valores, sin importar el tamaño de ``array``
    '''
    # if not is_even(array):
    #     print 'WARNING: el número de elementos en array no es par'
    scale = sample/float(array.size)
    fdt = np.fft.rfft(array)
    fourier_fit = np.fft.irfft(fdt[:amplitud], n=sample)*scale
    return fourier_fit
