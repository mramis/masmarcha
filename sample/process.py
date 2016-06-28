#!/usr/bin/env python
# coding: utf-8

'''Ensambla en tres funciones el proceso de extracción, cálculo y visualización
de los datos que se obtinen, de al menos uno, de los archivos de texto plano que
genera como salida Kinovea sobre las trayectorias editadas en un video.
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

import os
import logging

import numpy as np

from lectura.extractArrays import textToArray
from lectura.lecturaExceptions import (BadFileError,
                                       BadTimeUnitError,
                                       BadOriginSets)
from calculo.joints import hipAngles, kneeAngles, ankleAngles, Direction
from calculo.interpolation import extendArraysDomain, interpolateArray
from plots.anglesPlot import AnglePlot
from documento.report import baseReport

logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.DEBUG)

def extractJointMarkersArraysFromFiles(files):
    '''Toma como parametros uno o más archivos de texto(path), que son salida de
        Kinovea, con la información de las trayectorias de puntos articulares
        específicos, luego incorpora esos datos a un diccionario cuyo nombre
        llave(key) es el nombre del archivo sin la extensión(.txt) y valor de
        la llave(value) es un arreglo ``numpy.array``, con los datos del archivo
    Args:
        Lista(list) de archivos de Kinovea output plain/text, con los resultados
        de la edición de las trayectorias del miembro inferior.
    Raises:
        Exception, si los archivos no son salida de Kinovea.
    Returns:
        Diccionario(dict), donde dict.keys() = ['file0, file1', ..., fileN'] y
        dict.values() = [np.array([t00, x00, y00], [t01, x01, x01], ...,
        [t0r, x0r, y0r]), np.array([t10, x10, y10], [t11, x11, y11], ...,
        [t1r, x1r, y1r]), ..., np.array([tN0, xN0, yN0], [tN1, xN1, yN1], ...,
        [tNr, xNr, yNr])], donde N es el número de archivos ingresados, y r es
        el número de datos que tiene cada trayectoria.
    '''
    output = {}
    for file_path in files:
        abs_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path).split('.', 1)[0]
        try:
            array = textToArray(abs_path)
        except BadFileError as error:
            logging.critical(error.message)
        except BadTimeUnitError as error:
            logging.critical(error.message)
        except BadOriginSets as error:
            logging.critical(error.message)
        output[filename] = array
    return output

def extractJointAnglesFromJointMarkersArrays(points_array):
    '''Toma un diccionario(dict) de arrays``points_array``, que es salida de la
        función ``extractJointMarkersArraysFromFiles`` y define cuatro puntos
        de posición como referencia para el cálculo de los ángulos: cadera,
        rodilla, tobillo y cabeza 5to metatarsiano. Si el número de
        trayectorias en el archivo es distinto de 4 se lanza una exepción
        (Exception).
        Del arreglo de datos de cada valor(value) de ``points_array``, calcula
        los ángulos articulares, y los almacena en un diccionario, cuyos valores
        llave(keys) son el nombre de la articulación y tienen como valores
        (values) un arreglo ``np.array`` de ángulos.
        Tiene como salida un diccionario, donde las llaves(keys) son las mismas
        que las del diccionario de entrada, y los valores(values) son estos
        diccionarios confeccionados con los nombres articulares y sus arreglos
        de datos.

    Args:
        Diccionario(dict) con los arreglos ``np.array`` de las trayecorias de 4
        puntos clave en mmii: cadera, rodilla, tobillo y 5to metatarsiano.
    Raises:
        Exception si el número de trayectorias encontradas en alguno de los
        arreglos es distinto de cuatro.
    Return:
        Diccionario cuyas llaves(keys) son las mismas llaves(keys) que las del
        argumento de entrada(``points_array.keys()``), y cuyos valores son
        diccionarios de "articulacion:arreglo_de_angulos".
    '''
    angles_array = {}
    for filename, array in points_array.iteritems():
        joints = {}
        try:
            hip_p, knee_p, ankle_p, foot_p = array
            direction = Direction(array)
            joints['hip'] = hipAngles(hip_p, knee_p, direction)
            joints['knee'] = kneeAngles(hip_p, knee_p, ankle_p, direction)
            joints['ankle'] = ankleAngles(knee_p, ankle_p, foot_p)
            angles_array[filename] = joints
        except ValueError:
            logging.critical('El número de marcadores es incorrecto')
            raise Exception
        except DirectionError as error:
            logging.critical(error.message)
    return angles_array

def plotJointAnglesArrays(angles_array, name=''):
    '''Genera 3 archivos *.png* con las gráficas de ángulos que se le pasan como
        argumento en ``angles_array``. Los archivos se guardan en el directorio
        corriente, bajo el nombre "hip_+``name``+.png", para el caso de la
        cadera, y homóloga forma para el resto de las articulaciones de rodilla
        y tobillo.
    Args:
        angles_array: Diccionario(dict) con llaves(keys) que llevan el nombre
            del archivo de texto que del que se leen los datos(Kinovea output
            plain/text), y cuyas valores(values) son, también, diccionarios que
            tienen como llaves el nombre de una articulacion(hip, knee, ankle) y
            como valores arreglos(``np.array``) de un rango de ángulos.
        name: deafult(''), es el nombre con que se va a guardar la imagen .png
            de la gráfica.
    Returns:
        None.
    '''

    hip = [joint['hip'] for __, joint in sorted(angles_array.items())]
    knee = [joint['knee'] for __, joint in sorted(angles_array.items())]
    ankle = [joint['ankle'] for __, joint in sorted(angles_array.items())]
    
    if len(hip) > 1: # or knee or ankle, all must've the same length
        fixed_hip, hip_domain = extendArraysDomain(*hip)
        fixed_knee, knee_domain = extendArraysDomain(*knee)
        fixed_ankle, ankle_domain = extendArraysDomain(*ankle)
        # overwritten the originals variables
        hip = [interpolateArray(array, hip_domain) for array in fixed_hip]
        knee = [interpolateArray(array, knee_domain) for array in fixed_knee]
        ankle = [interpolateArray(array, ankle_domain) for array in fixed_ankle]
    else:
        hip = np.array(((np.arange(hip[0].size), hip[0]),))
        knee = np.array(((np.arange(knee[0].size), knee[0]),))
        ankle = np.array(((np.arange(ankle[0].size), ankle[0]),))
        
    # starts plots

    legend_labels = sorted(angles_array.keys())
    upp_lim = int(max([np.max(array[1]) for array in hip])) + 10
    low_lim = int(min([np.min(array[1]) for array in hip])) - 5
    if upp_lim < 50:
        upp_lim = 50
    if low_lim > -20:
        low_lim = -20
    hip_plot = AnglePlot('{}_Cadera_'.format(name))
    hip_plot.configure(ylimits=(low_lim, upp_lim))
    for i, array in enumerate(hip):# Cuando se quiera incluir ajuste polinómico
                                   # debe hacerse en este sitio.
        hip_plot.buildTimeAnglePlot(array[1], array[0], name=legend_labels[i])
    hip_plot.savePlot()

    upp_lim = int(max([np.max(array[1]) for array in knee])) + 10
    low_lim = int(min([np.min(array[1]) for array in knee])) - 5
    if upp_lim < 70:
        upp_lim = 70
    if low_lim > -10:
        low_lim = -10
    knee_plot = AnglePlot('{}_Rodilla_'.format(name))
    knee_plot.configure(ylimits=(low_lim, upp_lim))
    for i, array in enumerate(knee):
        knee_plot.buildTimeAnglePlot(array[1], array[0], name=legend_labels[i])
    knee_plot.savePlot()

    upp_lim = int(max([np.max(array[1]) for array in ankle])) + 10
    low_lim = int(min([np.min(array[1]) for array in ankle])) - 5
    if upp_lim < 30:
        upp_lim = 30
    if low_lim > -40:
        low_lim = -40
    ankle_plot = AnglePlot('{}_Tobillo_'.format(name))
    ankle_plot.configure(ylimits=(low_lim, upp_lim))
    for i, array in enumerate(ankle):
        ankle_plot.buildTimeAnglePlot(array[1], array[0], name=legend_labels[i])
    ankle_plot.savePlot()

def buildReport(name, datos):
    '''Construye u documento .pdf con la información que se obtiene de toda la
    operación que realiza la aplicación.

    '''
    pdf = baseReport('{}.pdf'.format(name), **datos)
    pdf.drawHeader()
    pdf.drawFootPage()
    pdf.drawCharts()
    pdf.showPage()
    pdf.save()



if __name__ == '__main__':
    kinovea_files = [
            ('../test/kinoveatext/TPlano.txt'),
            ('../test/kinoveatext/MPlano.txt'),
    ]

    joint_markers_array = extractJointMarkersArraysFromFiles(kinovea_files)
    joint_angles_array = extractJointAnglesFromJointMarkersArrays(joint_markers_array)
    plotJointAnglesArrays(joint_angles_array, name='Mariano.123')

