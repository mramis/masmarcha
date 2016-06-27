#!usr/bin/env python
# coding: utf-8

'''Este módulo se utiliza para el cálculo de los angulos articulares durante
el movimiento de marcha en el plano sagital.
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


import numpy as np

from canonicalVectors import positiveX, negativeX
from calculations import Angle, Direction

def hipAngles(hipArray, kneeArray, direction):
    '''Calcula el ánguls de la articulación de la cadera con respecto a la
        línea vertical que pasa por la misma y el segmento del muslo, en la
        variación t(tiempo) del movimiento de la marcha.

        Los ángulos de cadera se calculan a través de la definición del producto
        escalar de vectores::
            u·v = |u||v|cos(theta), tomando a u=(1,0) ó u=(-1, 0) (depende de
            la variable ``direction``) y a v=muslo(orientado hacia abajo).
        
        Con la convención de que la flexión de cadera sucede cuando el muslo
        pasa por delante del la línea vertical que cae sobre la articulación,
        la extensión en la dirección contraria, y el valor nulo cuando está en
        la misma línea vertical.

    Args:
        hipArray: ``np.array`` de datos tiempo(t), posición(x), posición(y) del
        desplazamiento en el plano sagital de la cadera.
        kneeArray: ``np.array`` de datos tiempo(t), posición(x), posición(y) del
        movimiento en el plano sagital de la rodilla.
        direction: escalar, que determina el sentido(o dirección) de avance de
        la persona. Ver ``sample/calculo/calculations.py``.
    Returns:
        hipAngles: ``np.array`` con el resultado del cálculo.
    '''
    HAP = hipArray[:, 1:] # without time
    KAP = kneeArray[:, 1:] # same here
    assert isinstance(HAP, np.ndarray) and isinstance(KAP, np.ndarray)
    thigh = KAP - HAP
    if direction is 1:
        hipAngle = 90 - Angle(thigh, positiveX(thigh.shape[0]))
    else:
        hipAngle = 90 - Angle(thigh, negativeX(thigh.shape[0]))
    return  hipAngle

def kneeAngles(hipArray, kneeArray, ankleArray, direction):
    '''Calcula el ángulo de la articulación de la rodilla con respecto a la
        a la posición angular relativa de la cadera(orientación del muslo), y el 
        segmento de la pierna, en la variación t(tiempo) del movimiento de la 
        marcha.

        Los ángulos de rodilla se calculan a través de la definición del
        producto escalar de vectores::
            u·v = |u||v|cos(theta), tomando a u=(1,0) ó u=(-1, 0) (depende de
            la variable ``direction``) y a v=pierna(orientada hacia abajo);
            donde theta es el angulo que la pierna(tomado como vector) forma con
            el eje x(positivo o negativo) en un sistema cartesiano con origen en
            la rodilla.
            Luego el ángulo de la articulación de la rodilla se obtinene como
            la suma entre el ángulo de cadera y el ya mencionado theta.
        
        Con la convención de que la flexión de rodilla sucede cuando la pierna
        pasa por detrás del la línea que se continua del muslo, la extensión en
        dirección contraria, y el valor nulo cuando está en la misma línea del
        muslo.

    Args:
        hipArray: ``np.array`` de datos tiempo(t), posición(x), posición(y) del
        desplazamiento en el plano sagital de la cadera.
        kneeArray: ``np.array`` de datos tiempo(t), posición(x), posición(y) del
        movimiento en el plano sagital de la rodilla.
        ankleArray: ``np.array`` de datos tiempo(t), posición(x), posición(y)
        del movimiento en el plano sagital del tobillo.
        direction: escalar, que determina el sentido(o dirección) de avance de
        la persona. Ver ``sample/calculo/calculations.py``.
    Returns:
        kneeAngles: ``np.array`` con el resultado del cálculo.
    '''
    KAP = kneeArray[:, 1:]
    AAP = ankleArray[:, 1:]
    assert isinstance(AAP, np.ndarray)
    leg = AAP - KAP
    hipAngle = hipAngles(hipArray, kneeArray, direction)
    if direction is 1:
        lowKneeAngle = Angle(leg, positiveX(leg.shape[0])) - 90
    else:
        lowKneeAngle = Angle(leg, negativeX(leg.shape[0])) - 90
    kneeAngle = lowKneeAngle + hipAngle
    return kneeAngle

def ankleAngles(kneeArray, ankleArray, mttArray):
    '''Calcula el ángulo de la articulación del tobillo con respecto a los
        segmentos de pierna y pie, en la variación t de tiempo durante el
        movimiento de la marcha.

        El ángulo de tobillo se calculan a través de la definición del 
        producto escalar de vectores::
            u·v = |u||v|cos(theta), tomando a u=pierna(orientado hacia arriba)
            y a v=pie(orientado hacia delante).
        
        Con la convención de que la flexión de tobillo sucede cuando el pie se
        acerca por delante hacia la pierna, la extensión en la dirección 
        contraria, y el valor nulo cuando el segemento de la pierna y el pié se
        encunetran formando un águlo recto.

    Args:
        kneeArray: ``np.array`` de datos tiempo(t), posición(x), posición(y) del
            movimiento en el plano sagital de la rodilla.
        ankleArray: ``np.array`` de datos tiempo(t), posición(x), posición(y)
            del movimiento en el plano sagital del tobillo.
        mttArray: ``np.array`` de datos tiempo(t), posición(x), posición(y) del
            movimiento en el plano sagital de la cabeza del 5 metatarsiano.
    Returns:
        ankleAngles: ``np.array`` con el resultado del cálculo.
    ''' 
    KAP = kneeArray[:, 1:]
    AAP = ankleArray[:, 1:]
    MAP = mttArray[:, 1:]
    assert isinstance(MAP, np.ndarray)
    leg = KAP - AAP
    foot = MAP - AAP
    ankleAngle = 90 - Angle(leg, foot)
    return ankleAngle

