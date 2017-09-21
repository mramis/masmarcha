#!/usr/bin/env python
# coding: utf-8

"""Docstring."""

# Copyright (C) 2017  Mariano Ramis

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

import cv2
import numpy as np
from video import centroid


def center_of_square(contour):
    u"""Centro de cuadrado.

    Devuelve el centro del cuadrado que encierra los marcadores de la image.
    :param contour: objeto contorno del marcador.
    :type contour: cv2.findContours
    :return: int, int: (x, y) centro del contorno.
    :rtype: tuple
    """
    return centroid(*cv2.boundingRect(contour))


def image_proccess(frame):
    u"""Procesamiento de la imagen.

    Cada cuadro de video es convertido a escala de gris y luego binarizado, tal
    que solo quedan en el cuadro las regiones con umbral de blanco > 240. La
    función devuelve un arreglo con los centros de estas regiones y el número
    de regiones encontradas.
    :param frame: cuadro de la imagen.
    :type frame: np.ndarray
    :return: int:número de marcadores y np.array: centro de las regiones.
    :rtype: tuple
    """
    kernel = np.ones((5, 5), np.uint8)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dilation = cv2.dilate(gray, kernel, iterations=1)
    binary = cv2.threshold(dilation, 240., 255., cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(binary,
                                cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
    mark = np.array(map(center_of_square, contours[1]))
    return mark.shape[0], mark


def roi_center(array, amp=1.4):
    u"""Región de interes.

    Calcula límites de región según el arreglo de posiciones y la amplitud que
    se pasa en el argumento. Toma las fronteras verticales del arreglo y los
    amplia según el factor amplitud.
    :param array: grupo de centros de marcadores(posiciones).
    :type array: np.ndarray
    :return: int, int: (ya, yb) los limites superior e inferior del grupo,
    ampliados.
    :rtype: tuple
    """
    y1 = array[0][1]
    y2 = array[-1][1]
    dy = (y1 - y2)*amp
    center = (y1 + y2) / 2
    return(center - dy, center + dy)


def grouping(markers, n_expected, kroi=False):
    u"""Agrupamiento.

    Esta función agrupa los centros de marcadores, con el objetivo de disminuir
    los datos que se pierden y por tanto, los que tienen que ser interpolados.
    Los tres grupos son G0: los marcadores de tronco y muslo superior, G1: los
    marcadores de la región de rodilla, y G2: los marcadores de la región de
    tobillo.
    La función acepta como argumento opcional la zona de interes de la rodilla
    (ver roi_center) que establece los grupos cuando el número de marcadores es
    distinto al esperado.
    :param markers: marcadores(centros) obtenidos del proceso del videoframe.
    :type markers: np.ndarray
    :param n_expected: (int, int, int): arreglo con el número de marcadores
    esperados por grupos.
    :type n_expected: tuple
    :return: (list, tuple): lista de booleanos que indica los grupos que tienen
    que ser interpolados, y tupla con los grupos (G0, G1, G2) siendo Gi un
    np.ndarray.
    :rtype: tuple
    """
    if kroi:
        Y = markers[:, 1]
        G0 = markers[Y < kroi[0]]
        G1 = markers[np.logical_and(Y > kroi[0], Y < kroi[1])]
        G2 = markers[Y > kroi[1]]
    else:
        G0 = markers[5:, :]
        G1 = markers[3:5, :]
        G2 = markers[:3, :]
    n_obtained = (G0.shape[0], G1.shape[0], G2.shape[0])
    boolean_interpolate = [a != b for a, b in zip(n_expected, n_obtained)]
    return(boolean_interpolate, (G0, G1, G2))


def diff(array, dt=1):
    u"""Diferencia consecutiva.

    Calcula la diferencia que existe entre el (i+1)ésimo y i-ésimo termino de
    un arreglo consecutivo de datos. El argumento dt, por defecto unitario, es
    la distancia que existe entre la sucesión de estos términos.
    :param array: arreglo dim=1, de terminos.
    :type array: (tuple or list)
    :return: arreglo de las diferencias.
    :rtype: list
    """
    vel = []
    for prev, new in zip(array[:-1], array[1:]):
        if prev and new:
            vel.append((new - prev) / dt)
        else:
            vel.append(None)
    vel.append(dt)  # este ultimo es arbitrario, pero no puede ser 0 o None
    return vel


def foot_direction(foot_group):
    u"""Establece la orientación del pie en el eje de las x.

    Toma como referencia el marcador de talón y el marcadore de antepié
    del grupo de tobillo.
    :param foot_group: grupo de marcadores de tobillo.
    :type: np.ndarray
    :return: -1 si orienta en el sentido negativo de las x, 1 si es el
    opuesto.
    :rtype: int
    """
    x_antepie = foot_group[0, 0]
    x_talon = foot_group[1, 0]
    if x_talon < x_antepie:
        return 1
    else:
        return -1


def sort_foot_markers(foot, direction=False):
    u"""Ordenamiento de los marcadores del pie.

    Cuando se toman los marcadores del videoframe en la función image_proccess
    los marcadores se ordenan por nivel de filas(y), por lo tanto, durante la
    marcha los marcadores de pie y talón pueden verse intercambiados varias
    veces durante un mismo ciclo. Si se pasa el argumento de dirección,
    entonces los marcadores se ordenan por sus valores xtalon, xantepié. Si no
    se pasa este argumento entonces el ordenamiento se produce con el xtobillo,
    pero en este caso solo se vale cuando el pie se encuentra plano sobre el
    suelo.
    :param foot: arreglo de marcadores del grupo de tobillo.
    :type foot: np.ndarray
    :param direction: valor de dirección, por defecto False.
    :type direction: int, 1 or -1
    :return: arreglo de grupo tobillo ordenado: antepie, talon y maleolo
    :rtype: np.ndarray
    """
    if foot.shape[0] != 3 and direction:
        return None
    x1, x2, refer = foot[:, 0]
    if direction:
        if direction > 0:
            if x1 < x2:
                talon = foot[0]
                antepie = foot[1]
            else:
                talon = foot[1]
                antepie = foot[0]
        elif direction < 0:
            if x1 < x2:
                talon = foot[1]
                antepie = foot[0]
            else:
                talon = foot[0]
                antepie = foot[1]
    else:
        values = ((abs(refer - x1), 0),
                  (abs(refer - x2), 1))
        talon = foot[min(values)[1]]
        antepie = foot[max(values)[1]]
    maleolo = foot[-1]
    return np.array((antepie, talon, maleolo))


def set_direction(foot_markers, M=3):
    u"""Determina la dirección en la se mueve la persona.

    Toma los marcadores de tobillo y los ordena cuando el pie no está
    cambiando de posición, entonces determia la orientación del pie. Se
    establece la dirección del movimiento por el signo de la suma
    de las orientaciones de pié.
    :param foot_markers: arreglo de marcadores del grupo de tobillo.
    :type foot_markers: np.ndarray
    :param M: número de marcadores que se espera encontrar en el grupo.
    :type M: int
    :return: dirección, -1 si se mueve en el sentido negativo de las x y 1
    en el caso opuesto.
    :rtype: int
    """
    Y = map(lambda m: m[0][1]
            if (isinstance(m, np.ndarray) and m.shape[0] != 0)
            else np.random.randint(0, 1000),
            foot_markers)
    vel = diff(Y)
    direction = 0
    for v, arr in zip(vel, foot_markers):
        if v == 0 and arr.shape[0] == M:
            sorted_foot = sort_foot_markers(arr)
            direction += foot_direction(sorted_foot)
    return 1 if direction > 0 else -1


def linear(x, x1, x2, y1, y2):
    u"""Función lineal.

    Determina el valor de y = (y2 - y1)*(x - x1)/(x2 - x1) + y1
    :param x1, y1: punto sobre una recta.
    :param x2, y2: punto sobre una recta.
    :param x: valor de x
    :type x, x1, x2, y1, y2: int
    :return: y = f(x)
    :rtype: int
    """
    num = (x - x1)*(y2 - y1)
    div = (x2 - x1)
    if not div.all():
        return (y2 + y1) / 2
    return num / div + y1


def interpolate(A, B, n_steps):
    u"""Realiza una interpolación lineal entre los arreglos A y B.

    :param A: arreglo de marcadores inicial.
    :type A: np.ndarray
    :param B: arreglo de marcadores final.
    :type B: np.ndarray
    :param n_steps: cantidad de datos que se necesita entre A y B.
    :type n_steps: int
    :return: lista de arreglos de tamaño n_type que se encuentran entre A y B.
    :rtype: list
    """
    n_steps += 1
    x1, y1 = A.T
    x2, y2 = B.T
    dx = np.round((x2 - x1) / float(n_steps))
    interpolated = []
    for n in xrange(1, n_steps):
        X = x1 + dx*n
        Y = linear(X, x1, x2, y1, y2)
        interpolated.append(np.array((X, Y), dtype=int).T)
    return interpolated


def interval(index_to_interpolate):
    u"""Intervalo de interpolación.

    Los datos faltantes en la lectura del videoframe son interpolados
    por una función lineal, entre dos extremos de datos completos. Los
    índices de los cuadros de datos faltantes se extraen en el agrupamiento
    de datos, y en este nivel se generan los extremos de los intrevalos
    de índices consecutivos por grupo.
    :param index_to_interpolate: Los indices de los datos faltantes.
    :type index_to_interpolate: list or tuple
    :return: tuplas con extremos de intervalos a interpolar (a, b)
    :rtype: generator
    """
    if not index_to_interpolate:
        return
    index = [x for x in index_to_interpolate]
    Xi = index.pop(0)
    if not index:
        yield Xi-1, Xi+1
        return
    it = []
    it.append(Xi)
    for i, Xj in enumerate(index):
        if (Xj - Xi) > 1:
            yield it[0] - 1, it[-1] + 1
            it = [Xj]
        else:
            it.append(Xj)
        Xi = Xj
    yield it[0] - 1, Xj + 1


def homogenize(binary, iterations=5):
    u"""Homogeneizar.

    Cuando se quieren determinar las fases de apoyo y balanceo dentro
    del ciclo, se toma como parámetro la velocidad de los marcadores
    de talón y pie.
    Esta función toma el arreglo de datos de 0 y 1 (apoyo y balanceo)
    filtra los valores distintos de cero dentro del intervalo de apoyo
    (primer 0, ultimo 0), pués existen pequeños momentos distinto de
    0 dentro del intervalo mencionado.
    :param binary: arreglo con las velocidades de talón y tobillo de
    dos valores posibles (0, 1) para las condiciones de apoyo y balanceo.
    :type binary: list
    :param iterations: máximo número de valores consecutivos distinto de
    0(cero), que se espera, contenga la fase de apoyo.
    :type param: int
    :return: None
    """
    kernel = 1
    for __ in xrange(iterations):
        for i, value in enumerate(binary):
            binary[i] += kernel + 1
            kernel = value
        for i, value in enumerate(binary):
            if value == 1:
                binary[i] = 0
    for i, value in enumerate(binary):
        if value == 0:
            for j in xrange(1, iterations + 1):
                binary[i - j] = 0
        else:
            binary[i] = 1


def mov_validation(foot_movement, cycle):
    u"""Validar velocidad armónica en los marcadores de pie."""
    validate = 0
    for movement in foot_movement:
        movcopy = movement[cycle[0][0]: cycle[1][1]]
        temp = movcopy.pop(movcopy.index(max(movcopy)))
        level = temp * 0.5  # DEBUG(HARDCORE): se setea un nivel alto.
        for j in xrange(5):
            M = movcopy.pop(movcopy.index(max(movcopy)))
            if (temp - M) < level:
                if j == 0:
                    validate += 1
                break
            temp = M
    if validate == 2:
        return True, cycle
    else:
        return False, None


def angle(A, B):
    """Calcula el ángulo(theta) entre dos vectores.

    Según la definición de producto escalar: u·v = |u||v|cos(theta)
    :param A: arreglo de vectores fila con las posiciones x, y respectivamente
    de un punto en el plano.
    :type A: np.ndarray
    :param B: arreglo de vectores fila con las posiciones x, y respectivamente
    de un punto en el plano.
    :type B: np.ndarray
    :return: arreglo de ángulos en grados.
    :rtype: np.ndarray
    """
    NA = np.linalg.norm(A, axis=1)
    NB = np.linalg.norm(B, axis=1)
    AB = A.dot(B.T).diagonal()
    radians = np.arccos(AB / (NA * NB))
    return np.degrees(radians)


def fourierfit(array, sample=101, amplitud=4):
    u"""Devuelve una aproximación de fourier con espectro que se
    define en ``amplitud``. Por defecto la muestra es de 101
    valores, sin importar el tamaño de ``array``
    :param array: arreglo de angulos en grados.
    :type array: np.ndarray
    :param sample: número de muestras que se quiere obetener en el arreglo.
    :type param: int
    :param amplitud: los primeros n coeficientes de fourier que se
    utilizan el el cálculo.
    :type amplitud: int
    :return: arreglo con los datos de angulos ajustados por la serie de
    Fourier utilizando los primeros n=amplitud terminos, de tamaño
    dim(array.rows, sample)
    :rtype: np.ndarray
    """
    scale = sample/float(array.shape[1])
    fdt = np.fft.rfft(array)
    fourier_fit = np.fft.irfft(fdt[:, :amplitud], n=sample)*scale
    return fourier_fit


def convert_px_cm(cmreference, pxdistance, cmscale=30.):
    u"""Convertir pixeles a centímetros.

    Esta función se utiliza para pasar la unidad de pixeles de videframe a
    unidad de centímtros.
    :param cmreference: distancia en centímetros.
    :type cmreference: float
    :param pxdistance: distancia en pixeles.
    :type pxdistance: int
    :param cmscale: es la relación entre cm y pixeles que se está tomando
    para el video.
    :type cmscale: float
    :return: conversión de pixeles a centimetros.
    :rtype: float
    """
    if not cmreference:
        return 0
    return pxdistance * cmscale / cmreference


def metric_reference(metrics):
    u"""Obtener referencias de unidad metrica.

    Esta función recibe las posiciones de los marcadores de referencia que
    se activan durante la primer parte del video. Devuelve la distancia media
    (en pixeles) que existe entre ellos para poder convertir esta medida a
    centímetros.
    :param metrics: arreglo de pocisión de marcadores de referencia.
    :type metrics: np.ndarray
    :return:
    """
    if not metrics.any():
        return 0
    distances = []
    X = np.sort(metrics[:, 0])
    for P0, P1 in zip(X[:-1], X[1:]):
        distances.append(abs(P0 - P1))
    return np.mean(distances)


def RMSE(X1, X):
    u"""Raiz del error cuadrático medio.

    Calcula el error cuadrático medio entre dos arreglos de la misma
    cantidad de datos. Se utiliza como medida de aproxiamción entre
    los valores de angulos que se obtinen y los valores normales.
    :param X1: arreglo de angulos.
    :type X1: np.ndarray
    :param X: arreglo de angulos normal.
    :type X: np.ndarray
    :return: ECM
    :rtype: float
    """
    return np.sqrt(np.sum(np.power(X1 - X, 2))/X.shape[0])


def positiveX(RowDim):
    array = np.zeros((RowDim, 2))
    array.T[0] = 1
    return array


def negativeX(RowDim):
    array = np.zeros((RowDim, 2))
    array.T[0] = -1
    return array
