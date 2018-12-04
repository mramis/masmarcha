#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2018  Mariano Ramis

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


import logging
import numpy as np


def soften(arr, loops=10):
    for i in range(loops):
        pos = 1
        for pre, post in zip(arr[0:-2], arr[2:]):
            arr[pos] = np.mean((pre, post))
            pos += 1
    return(arr)


def gait_cycler(markers, schema, cyclers=("M5", "M6"), threshold=2.5,
                safephase=10):
    u"""Busca si existen ciclos de apoyo y balanceo en la caminata.

    La función busca si existen ciclos de marcha, apoyo y balanceo, dentro
    de la caminata. Utiliza los centros de los marcadores del pie a través
    del cambio de velocidad de dichos marcadores.
    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    :param cyclers: son los índice de fila (marcadores) en los que se
     tiene que tomar la velocidad. Por defecto son los últimos dos, que se
     corresponden con los del pié según el diagrama del esquema. El vector
     cyclers siempre tiene que ser de dimensión 2 de otra manera se
     lanzará una exepción. Los argumentos del vector pueden ser el mismo
     componente (ej: ("M5", "M5")).
    :type cyclers: tuple
    :param threshold: Es el umbral que se toma para separar el apoyo del
     balanceo.
    :type threshold: float
    :return: vector que contiene una lista de ciclos, el arreglo de velocidad
     media de los centros de marcadores de pie, y el arreglo de datos boleanos
     de movimiento.
    :rtype: tuple
    """
    # Se toman los índices de los marcadores según el diagrama de esquema.
    # Si en el argumento cy_markers se pasa un solo valor, entonces se
    # duplica el índice para que la función np.mean que se toma después de
    # aplicar la función np.gradient no lanze una excepción por el kwarg
    # "axis".
    ix = [k for k, m in enumerate(schema['markerlabels']) if m in cyclers]
    if len(ix) == 1:
        ix += ix
    # La media de la derivada de posicion en x e y de los marcadores de retro
    # (-2) y ante pie (-1). El valor absoluto es porque solo estoy interesado
    # en cuando toma valor cero o distinto de cero.
    diff = np.abs(np.gradient(markers[:, ix, :], axis=0).mean(axis=2))
    soften(diff.transpose()[0])
    soften(diff.transpose()[1])

    mov = np.logical_and(*(diff >= threshold).transpose())

    st = []  # stance
    cycles = []
    for i, (pr, nx) in enumerate(zip(mov[:-1], mov[1:])):
        # si el pie en el primer cuadro, de esta comparación, está en
        # movimiento y el próximo no lo está, entonces en el próximo cuadro el
        # pié se pone en contacto con el suelo.
        if pr and not nx:
            st.append(i+1)
        # si el pie en el primer cuadro no está en movimiento pero si lo está
        # en el próximo, entonces en el próximo cuadro el pié se despega del
        # suelo.
        if not pr and nx:
            tf = i+1  # toeoff
        # siempre que haya dos apoyos, hay un ciclo.
        if len(st) == 2:
            # NOTE: Cuando se marca un ciclo se corrobora que la distancia
            # entre moemntos de fases cumpla con un mínimo. Para darle
            # flexibilidad vamos a hacer que ese mínimo pueda ser regulado por
            # el usuario.
            if (tf - st[0]) > safephase and (st[1] - tf) > safephase:
                cycles.append(np.array((st[0], tf, st[1])))
            else:
                logging.error("""Cinemática. Ciclo, diferencia de cuadros entre
                fases demasiado corta (<{})""".format(safephase))
            st.pop(0)
    return (diff, mov, cycles)


def get_direction(markers, schema):
    u"""La dirección de la caminata.

    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    :return: valor de dirección.
    :rtype: int
    """
    # Se utilizan los marcadores de pie para obtener la dirección de avance
    foot = schema['segments']['foot']
    ix = [k for k, m in enumerate(schema['markerlabels']) if m in foot]
    # El vector que representa al segmento del pié es la diferencia del
    # marcador del antepié con la del retropié.
    xrfoot, xffoot = markers[:, ix, 0].transpose()
    # La dirección es la media de las distancias en x entre el pie anterio y el
    # pie posterior. Si este número es mayor que cero, entonces avanza en
    # sentido positivo de las x y el lado que se evalua es el derecho, de otra
    # forma es izquierdo.
    return int((xffoot - xrfoot).mean(axis=0) > 0)


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


def positiveX(shape):
    u"""arreglo de vectores unitarios.

    Estos vectores tienen módulo unitario y dirección positiva en el eje de las
    x.
    """
    array = np.zeros(shape)
    array[:, 0] = 1
    return array


def negativeX(shape):
    u"""arreglo de vectores unitarios.

    Estos vectores tienen módulo unitario y dirección negativa en el eje de las
    x.
    """
    array = np.zeros(shape)
    array[:, 0] = -1
    return array


def hip_joint(tight, canonical):
    u"""Angulos de la articulación de cadera.

    :param tight: arreglo vectores representantes de muslo. El vector tiene la
     orientación "céfalo-caudal"
    :type tight: np.array
    :param canonical: arreglo de vectores unitarios canonicales fila. Este
     vector tiene la dirección de avance del sujeto.
    :type canonical: np.array
    :return: arreglo de angulos de cadera.
    :rtype: np.array
    """
    return 90 - angle(tight, canonical)


def knee_joint(tight, leg, canonical):
    u"""Angulos de la articulación de rodilla.

    :param tight: arreglo vectores representantes de muslo. El vector tiene la
     orientación "céfalo-caudal"
    :type tight: np.array
    :param leg: arreglo vectores representantes de pierna. El vector tiene la
     orientación "céfalo-caudal"
    :type leg: np.array
    :param canonical: arreglo de vectores unitarios canonicales fila. Este
     vector tiene la dirección de avance del sujeto.
    :type canonical: np.array
    :return: arreglo de angulos de rodilla.
    :rtype: np.array
    """
    hip = hip_joint(tight, canonical)
    return hip + angle(leg, canonical) - 90


def ankle_joint(leg, foot):
    u"""Angulos de la articulación de tobillo.

    :param leg: arreglo vectores representantes de pierna. El vector tiene la
     orientación "caudo-cefálico"
    :type leg: np.array
    :param foot: arreglo vectores representantes de pie. El vector tiene la
     orientación "céfalo-caudal"
    :type foot: np.array
    :return: arreglo de angulos de tobillo.
    :rtype: np.array
    """
    return 90 - angle(leg * -1, foot)


def calculate_angles(markers, direction, schema):
    u"""Calculo de angulos durante el ciclo de marcha.

    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    :param direction: Valor de sentido de avance de la marcha.
    :type direction: int
    :return: arreglo de ángulos según el diagrama de esquema.
    :rtype: np.array
    """
    # Se organizan los marcadores según los códigos diagramados en el esquema.
    # Si bien se toma todo el arreglo de marcadores de la caminata, solo se
    # produce el cálculo de ángulos con los cuadros que pertenecen a un ciclo.
    dmarkers = {}
    for i, m in enumerate(schema['markerlabels']):
        # dmarkers[m] = markers[istrike: fstrike, i, :]
        dmarkers[m] = markers[:, i, :]

    # Se forman los segmentos según lo diagramado en el esquema.

    dsegments = {}
    for s, (a, b) in schema['segments'].items():
        dsegments[s] = dmarkers[b] - dmarkers[a]
    # Se calcula los ángulos siguiendo el diagrama del esquema.
    langles = []
    # La dirección de avance se toma de la dirección del pie. Se hace un
    # promedio del valor de las x, que indica si el pie se mueve en sentido
    # positivo o negativo con el eje x. Este valor entero, que puede ser "0" o
    # "1" se utiliza para seleccionar la función con la que se produce un
    # arreglo de vectores unitarios canonicales. Este arreglo se utiliza para
    # calcular el ángulo de cadera, (y de forma indirecta rodilla)
    tight = dsegments['tight']
    dsegments['canonical'] = (negativeX, positiveX)[direction](tight.shape)
    # Se agrupan las funciones que calculan los angulos en un diccionario para
    # que el proceso sea ordenado por el esquema.
    joint_functions = {
        'hip': hip_joint,
        'knee': knee_joint,
        'ankle': ankle_joint
    }
    # Lo mismo sucede con los argumentos que necesitan las funciones que
    # calculan los ángulos.
    joint_functions_args = {
        'hip': ('tight', 'canonical'),
        'knee': ('tight', 'leg', 'canonical'),
        'ankle': ('leg', 'foot')
    }
    # Se calculan los ángulos para cada articulación según lo diagramado en el
    # esquema.
    for j in schema['joints']:
        segments = [dsegments[i] for i in joint_functions_args[j]]
        langles.append(joint_functions[j](*segments))
    return np.array(langles)


def resize_angles_sample(angles, sample):
    u"""Modifica el tamaño de la muestra de ángulos.

    La función modifica el tamaño del arreglo, en cada vector de ángulos, a la
    cantidad de elementos que se pasa como argumentos de angles.

    :param angles: arreglo de ángulos fila.
    :type angles: np.array
    :param sample: tamaño al que se quiere llevar a cada vector de ángulos
     dentro del arreglo.
    :return: arreglo de ángulos cuya cantidad de componentes ha sido modificada
     por un proceso de interpolación lineal.
    :rtype: np.array
    """
    # Se modifica la cantidad de elemento del dominio de x al tamaño de sample.
    x = np.linspace(0, angles.shape[1], sample)
    # El dominio original del arreglo de ángulos.
    xs = np.arange(angles.shape[1])
    resized = []
    # Por cada articulación se hace una interpolación lineal por cada elemento,
    # nuevo en el dominio de x para aumentar el tamaño de la muestra a "sample"
    for joint in angles:
        resized.append(np.interp(x, xs, joint))
    return np.array(resized)


def fourier_fit(angles, sample, fft_scope=4):
    u"""Devuelve una aproximación de fourier con espectro que se
    define en ``fft_scope``. Por defecto la muestra es de 101
    valores, sin importar el tamaño de ``angles``
    :param angles: arreglo de angulos en grados.
    :type angles: np.ndarray
    :param sample: número de muestras que se quiere obetener en el arreglo.
    :type param: int
    :param fft_scope: los primeros n coeficientes de fourier que se
    utilizan el el cálculo.
    :type fft_scope: int
    :return: arreglo con los datos de angulos ajustados por la serie de
    Fourier utilizando los primeros n=fft_scope terminos, de tamaño
    dim(angles.rows, sample)
    :rtype: np.ndarray
    """
    scale = sample/float(angles.shape[1])
    fdt = np.fft.rfft(angles)
    fourier_fit = np.fft.irfft(fdt[:, :fft_scope], n=sample)*scale
    return fourier_fit


def calculate_spatiotemporal(cycle, markers, fps, pixel_scale):
    u"""Cálculo de los parámetros espacio temporales.

    :param cycle: índices de los cuadros que contienen un ciclo dentro de la
     caminata
    :type cycle: tuple
    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param fps: cuadros por segundos.
    :type fps: float
    :param pixel_scale: escalar para la conversión de distancia.
    :type pixel_scale: float
    :return: parámetros espacio-temporales: (duracion ciclo[m],
     fase de apoyo[%], fase de balanceo[%], zancada[m], cadencia[p/min],
     velocidad media[m/s]).
    :rtype: tuple
    """
    # la duración en segundos,
    istrike, swing, fstrike = cycle
    # Se calcula la duración en cuadros
    framesduration = float(fstrike - istrike)
    # la duración en segundos.
    duration = framesduration / fps
    # la longitud de zancada.
    # NOTE: La distancia está en metros. Si no se obtuvo el escalar de
    # conversión pixel_scale, entonces la distancia de zancada toma valor 0.
    stride = np.linalg.norm(markers[-1, -2] - markers[0, -2])*pixel_scale
    # Las unidades de los parámetros son: (s, %, %, m, pasos/min, m/s)
    return np.array((duration,
                     (swing - istrike) / framesduration * 100,
                     (fstrike - swing) / framesduration * 100,
                     stride,
                     120 / duration,
                     stride / duration))


def calculate_pixelscale(markers, legdistance):
    div = np.linalg.norm(markers[:, 3] - markers[:, 4], axis=1).mean()
    return(legdistance / div)


def calculate(walks, schema, threshold, fps, legdistance):
    u"""Generador de datos de marcha."""
    for e, w in enumerate(walks):
        markers = w.get_markers()
        # NOTE: COMPLETAR LOS ARGUMENTOS DE GAITCYCLER!
        __, __, cycles = gait_cycler(markers, schema, threshold=threshold)
        direction = get_direction(markers, schema)
        for c, (i, j, k) in enumerate(cycles):
            codename = '{}C{}'.format(w, c)
            scale = calculate_pixelscale(markers, legdistance[direction])
            stp = calculate_spatiotemporal((i, j, k), markers[i:k], fps, scale)
            ang = calculate_angles(markers[i:k], direction, schema)
            ang = resize_angles_sample(ang, 101)
            yield (codename, direction, stp, ang)
