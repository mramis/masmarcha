#!/usr/bin/env python
# coding: utf-8

"""Módulo para la extracción de información de los archivos de exportación del
software Kinovea.
"""

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


import re
from numpy import array


class KinoveFile(object):
    u"""Lectura de los archivos de texto que exporta kinovea."""

    def __init__(self, path):
        with open(path) as fh:
            self._file = fh.read().replace(',', '.')
        self.asignar_articulaciones()

    def bloques(self):
        u"""Cuenta el numero de bloques de datos en el archivo."""
        totem = '0:00:00:00'
        return len(re.findall(totem, self._file))

    def asignar_articulaciones(self):
        u"""Extrae la información del archivo.txt en marcadores."""
        code = {
            3: ['rodilla', 'tobillo', 'pie'],
            4: ['cadera', 'rodilla', 'tobillo', 'pie'],
            5: ['tronco', 'cadera', 'rodilla', 'tobillo', 'pie']
        }
        sg = code[self.bloques()]
        data = [row.split() for row in self._file.split('\n')]
        indexes = [n for n, l in enumerate(data) if l == []]
        indexes.insert(0, 1)  # Nivel de header.
        self.markers = []
        while indexes != []:
            i = indexes.pop(0)
            j = indexes.pop(0)
            marker = Marker(sg.pop(0))
            time, x, y = array(data[i+1:j]).transpose()
            marker.t = array(map(self.formato_tiempo, time))
            marker.x = array(map(float, x))
            marker.y = array(map(float, y))
            self.markers.append(marker)

    def formato_tiempo(self, time):
        u"""Transforma la secuencia de tiempo en punto flotante (segundos).

        :param time: Estructura de tiempo de kinovea "0:00:00:00".
        :type time: str
        """
        __, mm, ss, cc = time.split(':')
        return float(mm) * 60 + float(ss) + float(cc) / 100.


class Marker(object):
        u"""Marcador de referencia."""

        def __init__(self, pos):
            u"""Inicializa el marcador con la posición donde se situa.

            :param pos: Posición del marcador.
            """
            self.pos = pos
            self.x = None
            self.y = None
            self.t = None


if __name__ == '__main__':
    k = KinoveFile('/home/mariano/Devel/masmarcha/test/kinoveatext/MCinta.txt')
