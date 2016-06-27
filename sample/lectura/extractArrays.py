#!usr/bin/env python
# coding: utf-8

'''Los archivos de texto plano que exporta Kinovea sobre las trayectorias editas
Tiene el siguiente formato:

    #Kinovea Trajectory data export
    #T X Y
    0:00:00:00 866.00 320.00 
    0:00:00:03 847.00 321.00 
    ...

    0:00:00:00 118.00 45.00 
    0:00:00:03 131.00 37.00 
    ...
    
En este módulo definen funciones que analizan archivos en busca de estas
características(si no lo encuentran se lanzan excepciones definidas en sample/
lectura/lecturaExceptions.py) y extraen los datos en forma de numpy array, donde
cada arreglo tiene la forma:
np.array([np.array([t0, x0, y0],
                   [t1, x1, y1],
                   [... .. ...])],
         [np.array([t0, x0, y0],
                   [t1, x1, y1],
                   [... .. ...])])
    donde t = Tiempo en céntimas de segundo, x e y son las coordenadas de
    posición en el plano evaluado(sagital); las coordenadas son, por defecto,
    en pixeles.
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
from lecturaExceptions import BadTimeUnitError, BadFileError, BadOriginSets

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

def isKinoveaFile(textfile):
    '''Comprueba que esté el encabezado(header) de Kinovea en el archivo.
    Args:
        textfile: Archivo de texto con el contenido de la trayectorias editadas
        en Kinovea (plain/text output).
    Returns:
        boolean: True or False, según corresponda al archivo correcto o no.
    '''
    with open(textfile) as fh:
        value = False
        if '#kinovea' in fh.read().lower():
            value = True
    return value

def textToArray(textfile):
    '''Extrae los arreglos de datos que se encuentran en el archivo como numpy
        Arrays.
    Args:
        textfile: Archivo de texto con el contenido de la trayectorias editadas
        en Kinovea (plain/text output).
    Raises:
        BadOriginSets: excepcion (Exception) personalizada que se lanza cuando
        los primeros valores de cada arreglo son cero al mismo tiempo. Esto
        sucede cuando no se edita el centro de origen de coordenadas en
        Kinovea.
    Returns:
        ``np.array`` con los datos del archivo de texto.
    '''
    if not isKinoveaFile(textfile):
        raise BadFileError(textfile)
    
    splitter = dataSplitter(textfile)
    with open(textfile) as fh:
        text_file_content = fh.read()
    
    # split the text data by zero time
    data_arrays = text_file_content.split(splitter)
    data_arrays.pop(0) # first and second line header

    # split each row from each array to lines components
    split_arrays = [array.split('\n') for array in data_arrays]
    
    # the neasted code here build numpy arrays from splitted arrays.
    arrays = []
    for array in split_arrays:
        x, y = array[0].split()
        if int(restructure(x)) == 0 and int(restructure(y)) == 0:
            raise BadOriginSets(textfile)
        newArray = []
        for i, line in enumerate(array):
            row = line.split()
            if row:
                if i == 0:
                    row.insert(0, splitter)
                newRow = []
                for item in row:
                    newRow.append(restructure(item))
                newArray.append(newRow)
        arrays.append(newArray)
    return NParray(arrays, dtype=float)

if __name__ == '__main__':
    _file = '../test/kinoveatext/bad_originSistem_file.txt'
    print(dataSplitter(_file))
    print(isKinoveaFile(_file))
    print(textToArray(_file))
