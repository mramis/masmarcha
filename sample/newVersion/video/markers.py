#!/usr/bin/env python
# coding: utf-8

'''Se define aquí una clase que almacena la posoción de los marcadores
que se leen en cada cuadro.
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


from __future__ import division
from collections import deque
import cPickle

import numpy as np

from interpolation import linear_interpolation_range

print '##MENSAJE DE ADVERTENCIA## antes de segui con cualquier avanza se tiene que revisar la interpolación que está generando errores #'


class markerscollections(object):

    def __init__(self):
        '''El objeto se incializa sin argumentos.
        '''
        self._deque = deque(maxlen=3000)
        self._frames = 0
        self._indexsuccessframes = []
        self._lostframes = 0
        self._emptyframes = 0

    def __repr__(self):
        return self._deque.__repr__()

    def __len__(self):
        return len(self._deque)

    def __getitem__(self, index):
        return self._deque[index]

    def introduce(self, element):
        '''Se llama a este método para introducir los elementos en la
        cola.
        Args:
            Cada elemento es un numpy array de dos dimensiones.
            Por convención, si el elemento es un cuadro falso, todas las
            entradas del arreglo son "0.", si el arreglo es una cuadro
            vacío, entonces todas sus entradas son "-1.".
            Se agrgan todos los elementos, pero se cuentan por separados
            según sean falsos, vacios, o correctos. Los índices de los
            elementos correctos se guardan en una lista.
        Return:
            None
        '''
        if not element.any():
            self._lostframes += 1
            self._deque.append(element)
        elif element.mean() == -1.:
            self._emptyframes += 1
            self._deque.append(element)
        else:
            self._frames += 1
            self._deque.append(element)
            self._indexsuccessframes.append(len(self._deque) - 1)

    def clearlastn(self, n=4):
        '''Vacía los últimos n elementos(por defecto son cuatro) agregados
        a la cola.
        '''
        for __ in xrange(n):
            self._deque.pop()
        print 'se ejecutó %s.clearlastn() para %f cuadros' %(self.__class__, n)

    def interpolate(self):
        '''Revisa toda la cola(deque) y interpola(método lineal) los cuadros
        que son considerados como falsos.
        Args:
            No recibe argumentos, pués utiliza la cola que fué incializada.
        Returns:
            MarkerCollections objeto(instance)
        '''
        interpolated_markers = markerscollections()
        first_index_non_empy_frame = self._indexsuccessframes[0]
        step = 0
        jump = 0
        for index, marker_array in enumerate(self._deque):
            if index <= first_index_non_empy_frame:
                interpolated_markers.introduce(marker_array)
            else:
                if marker_array.mean() == 0.0:
                # si es un cuadro falso con contenido a interpolar, entonces
                # se agrega pero tambien aumenta en una unidad la variable
                # step
                    step += 1
                    interpolated_markers.introduce(marker_array)
                elif marker_array.mean() == -1.0:
                # si es un cuadro vacio, donde no existen marcadores entonces
                # se agrega pero tambien se incrementan las variables step y
                # jump. Si jump llega a un valor de 5 entonces se reinicia la
                # variable step, porque significaria que no hay persona
                # marchando en el video.
                    jump += 1
                    step += 1
                    interpolated_markers.introduce(marker_array)
                    if jump >= 5:
                        step = 0
                else:
                # cuando el cuadro tiene marcadores, y ademas la variable step
                # es distinta de cero se deben borrar los ultimos "step"
                # cuadros, interpolar, y agregar los los cuadros interpolados
                # a la coleccion, setear la variable step en valor cero para
                # que en el próximo cuadro, probablemente exitoso, el bucle no
                # entre en el proceso de interpolación. Además se modifican
                # las variables estadísticas.
                # Si la variable step es igual a cero, entonces se agrega el
                # cuadro y el cuadro actual que contiene marcadores, se
                # convierte en el ultimo capaz de interpolar.
                    jump = 0
                    if step != 0:
                        interpolated_markers.clearlastn(step)
                        interpolated_markers._lostframes += -1*step
                        interpolated_markers._frames += step + 1
                        new_interpolated_markers = linear_interpolation_range(
                            temp_marker_array,
                            marker_array,
                            step
                            )
                        for new_array in new_interpolated_markers:
                            interpolated_markers.introduce(new_array)
                        interpolated_markers.introduce(marker_array)
                        step = 0
                    else:
                        interpolated_markers.introduce(marker_array)
                        temp_marker_array = marker_array 
        return interpolated_markers


    def merge(self, markerscoll):
        '''Combina dos colas distintas. Cada arreglo(elemento) es de dos
        dimensiones, se combinan en un solo arreglo los elementos con el mismo
        índice dentro de las colas, el que se pasa como argumento va al final.
        Args:
            MarkerCollections es un objeto de esta misma clase. Cada elemento
            de un markercollections es un arreglo de dos dimensiones.
        Raises:
            Exception si las colas tienen diferente cantidad de elementos.
        Returns:
            None
        '''
        if len(markerscoll._deque) == len(self._deque):
            for first, second in zip(self._deque, markerscoll._deque):
                print np.vstack((first, second))
        else:
            raise Exception('Diferentes cantidades de elementos')

    def stats(self):
        '''Devuelve un diccionario con la frecuencia relativa de los cuadros,
        correctos, falsos y vacios expresados en porcentaje.
        '''
        ttframes = self._frames + self._lostframes + self._emptyframes
        relative_f = self._frames / ttframes * 100
        relative_lf = self._lostframes / ttframes * 100
        relative_ef = self._emptyframes / ttframes * 100
        return {'SuccessFrames': '{:2.2f}%'.format(relative_f),
                'LoosesFrames': '{:2.2f}%'.format(relative_lf),
                'EmptyFrames': '{:2.2f}%'.format(relative_ef)}

    def dump(self, filename='sample.txt'):
        '''Guarda el objeto en un archivo que se pasa como argumento'''
        stats = {'-f': self._frames,
                 '-sf': self._indexsuccessframes,
                 '-lf': self._lostframes,
                 '-ef': self._emptyframes}
        with open(filename, 'w') as filehandler:
            cPickle.dump((self._deque, stats), filehandler)

    def load(self, filename='sample.txt'):
        '''Carga el objeto que se pasa como argumento'''
        with open(filename) as filehandler:
            data = cPickle.load(filehandler)
            self._deque = data[0]
            self._frames = data[1]['-f']
            self._indexsuccessframes = data[1]['-sf']
            self._lostframes = data[1]['-lf']
            self._emptyframes = data[1]['-ef']
