#!usr/bin/env python
# coding: utf-8

'''El archivo de texto plano de salida de la edición de trayectorias en Kinovea
tiene la siguiente forma:
    #Kinovea Trajectory data export
    #T X Y
    0:00:00:00 866.00 320.00 
    0:00:00:03 847,00 321,00 
    ...
Si se quieren transformar los datos numéricos en valores manejables, entonces
se tiene que arreglar la parte del tiempo(T) 0:00:00:00, y la parte de las
coordenadas(X e Y) que en algunos sistemas operativos el valor decimal se
representa con el signo ",".
En este módulo se definen funciones que solucionan estos problemas.
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

def dataToTime(data):
    '''Convierte el formato de tiempo que exporta Kinovea 'h:mm:ss:cc' en
    segundos.
    Args:
        ``str`` con el formato de tiempo 'h:mm:ss:cc'
    Returns:
        ``float`` tiempo expresado en segundos.
    '''
    h, mm, ss, cc = data.split(':')
    newTime = (float(h)/3600. + float(mm)/60. + float(ss) + float(cc)*0.01)
    return newTime

def dataToFloat(data):
    '''El valor numérico en Kinovea en su forma decimal, puede estar
    representado de la forma "12,34"; en tal caso se convierte a la forma
    "12.34".
    Args:
        ``str`` con valor numérico de la forma "12,34".
    Returns:
        ``float(data)``
    '''
    no_float = list(data)
    ent, dec = data.split(',')
    return float('{}.{}'.format(ent, dec))

def restructure(data):
    '''Transforma las variables de entrada en valores numéricos adecuados.
    Args:
        data: ``str`` representación de un valor nummérico.
    Returns:
        ``float`` or ``None``
    '''
    value = list(data)
    returnValue = None
    if ':' in value:
        returnValue = dataToTime(data)
    elif ',' in value:
        returnValue = dataToFloat(data)
    elif '.' in value:
        returnValue = float(data)
    return returnValue

