#!usr/bin/env python
# coding: utf-8

"""Se definen funciones para calcular el ángulo entre dos arreglos de vectores,
la determinación de la dirección de marcha sobre el plano, y el ajuste
polinomial de datos.
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

import numpy as np

from calculoExceptions import DirectionError


def Angle(A, B):
    """Calcula el ángulo(theta) entre dos arreglos de vectores(fila) según la
        definición de producto escalar:
            u·v = |u||v|cos(theta)
    Args:
        A: arreglo ``np.array`` de vectores fila con las posiciones x, y
            respectivamente de un punto en el plano.
        B: lo mismo que A
    Returns:
        arreglo ``np.array`` de ángulos en grados.
    """
    assert isinstance(A, np.ndarray) and isinstance(B, np.ndarray)
    normA = np.sqrt((A.dot(A.T).diagonal()))
    normB = np.sqrt((B.dot(B.T).diagonal()))
    pInternoAB = A.dot(B.T).diagonal()
    radiansAngle = np.arccos(pInternoAB / (normA * normB))
    return np.degrees(radiansAngle)

def Direction(MasterArray):
    """Determina la dirección del movimiento de la persona sobre el suelo
        haciendo un promedio de la diferencia del último y primer dato de los
        arreglos que se pasan en MasterArray(el arreglo que contiene todos los
        datos de posición que se extrajeron del archivo de texto plano de
        Kinovea.
    Args:
        MasterArray: arreglo de arreglos ``np.array`` que contiene los datos que
            se extraen del archivo de texto plano que es salida de la edición de
            trayectorias en Kinovea.
    Raises:
        DirectionError: Exception personalizada que se lanza cuando no puede
            encontrarse una dirección.
    Returns:
        ``int`` los dos posibles valores son ``1``(indica que la dirección de
            marcha es el mismo que el eje positivo de las x y que el miembro
            inferior evaluado es el derecho; o ``-1``(se significa lo contrario)
        """
    assert isinstance(MasterArray, np.ndarray)
    rows, columns = MasterArray.shape[0], 1
    Xdirection = np.ndarray((rows, columns))
    for index, array in enumerate(MasterArray):
        firstRow, lastRow = array[0], array[-1]
        Xdirection[index] = (lastRow - firstRow)[1]
    average = np.average(Xdirection)
    if average > 0:
        directionValue = 1
    elif average < 0:
        directionValue = -1
    else:
        raise DirectionError('Dirección indeterminada')
    return directionValue
