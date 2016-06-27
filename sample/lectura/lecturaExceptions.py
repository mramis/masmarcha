#!/usr/bin/env python
# coding: utf-8

'''Excepciones(Exception) personalizadas para manejar los errores en la lectura
de los archivos de salida texto/plano de las Trayectorias editadas en Kinovea.
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


class BadTimeUnitError(Exception):
    '''Se lanza cuando la configuración de tiempo de kinovea no es del tipo
    'h:mm:ss:cc'
    Args:
        File: el nombre(path) del archivo
    '''
    def __init__(self, File=None):
        message = 'Tiempo, configuración incorrecta: {}'
        self.message = message.format(File)
    def __str__(self):
        return self.message

class BadFileError(Exception):
    '''Se lanza cuando el archivo analizado no es del tipo texto/plano de
    Kinovea.
    Args:
        File: el nombre(path) del archivo
    '''
    def __init__(self, File=None):
        message = 'Entrada inválida: {}'
        self.message = message.format(File)
    def __str__(self):
        return self.mesagge

class BadOriginSets(Exception):
    '''Se lanza cuando no se configuró el origen del sistema de coordenadas en
    la edición de trayectorias en Kinovea.
    Args:
        File: el nombre(path) del archivo
    '''
    def __init__(self, File):
        message = 'Trayectorias, origen de sistema incorrecto: {}'
        self.message = message.format(File)
    def __str__(self):
        return self.message

if __name__ == '__main__':
    try:
        raise BadOriginSets('/home/mariano/test.js')
    except BadOriginSets as error:
        print error.message
