#!usr/bin/env python
# coding: utf-8
'''
    #Kinovea Trajectory data export
    #T X Y
    0:00:00:00 866.00 320.00 
    0:00:00:03 847.00 321.00 
    ...
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

from numpy import array as NParray

from fixData import restructure
from lecturaExceptions import BadTimeUnitError

def dataSplitter(textfile):
    '''Verifica que la forma de tiempo t=0 sea del tipo '0:00:00:00' que
        Kinovea tiene por defecto(no siendo la única). A través de este valor
        la aplicación va a separar los arreglos de datos.
    Args:
        textfile: Archivo de texto con el contenido de la trayectorias editadas
        en Kinovea (plain/text output).
    Raises:
        BadTimeUnitError: una Excepción persoanlizada que indica cuál es el
        nombre del archivo que causó la excepción.
    Return:
        '0:00:00:00', la cadena que se toma como particionador de datos.
    '''
    with open(textfile) as fh:
        for line in fh:
            if not '#' in line:
                splitter= line.split()[0]
                break
            else:
                splitter = None
    if splitter != '0:00:00:00':
        raise BadTimeUnitError(textfile)
    return splitter

def textToArray(textfile):
    splitter = dataSplitter(textfile)
    with open(textfile) as f:
        _file = f.read()
    print(_file)
#split the text data by zero time
    textArrayss = _file.split(splitter)
    textArrayss.pop(0) # the Kinovea introduction
# split each line(row) from each array to lines components
    linesArrays = [array.split('\n') for array in textArrayss]
# remove all empty data and keep with time, x & y components
    arrays = []
    for array in linesArrays:
        x, y = array[0].split()
        if x == 0 and y == 0:
            raise Exception('Error with origin axis edited on kinovea')
        newArray = []
        for i, line in enumerate(array):
            cell = line.split()
            if cell:
                if i == 0:
                    cell.insert(0, splitter)
                newCell = []
                for item in cell:
                    newCell.append(restructure(item))
                newArray.append(newCell)
        arrays.append(newArray)
    return NParray(arrays, dtype=float)

if __name__ == '__main__':
    _file = '../../test/kinoveatext/MPlano.txt'
    print dataSplitter(_file)
    textToArray(_file)
