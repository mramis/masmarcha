#!/usr/bin/env python
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


from collections import deque, defaultdict
from contextlib import contextmanager
import json
import os
# from threading import Thread
import cv2
import numpy as np


# TODO:
# [x] Agregar a la sección de configuración los argumentos que puede ingresar
# el usuario.
# [] Informacion de interpolación y suavizado.
# [] Implementar logging.
# [] Conversión de unidades de distancia.
# [] Calibración de la imagen.
# [] Revisar la documentación.


def find_markers(frame, image_threshold=240.0):
    u"""Encontar marcadores.

    La función se encarga de binarizar la imagen del cuadro de video y aplicar
    un filtrado de umbral para detectar los marcadores. Cuando lo hace devuelve
    un arreglo de contornos de cada uno de los marcadores.
    :param image_threshold: límite de luz blanca que toma como mínimo para
     aceptar los marcadores.
    :type image_threshold: float
    :return: conjunto de arreglo de contornos.
    :rtype: list
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, image_threshold, 255., cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(
        binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    return contours[1]


def marker_center(contour):
    u"""Devuelve los centros de los contorno del marcador."""
    x, y, w, h = cv2.boundingRect(contour)
    return x + w/2, y + h/2


def identifying_markers(stream, n_frames, schema, **kwargs):
    u"""Se obtienen e identifican los arreglos de marcadores.

    Esta función extrae los centros de marcadores ordenados en sentido
    descendente, de la forma en la que está diagramado el esquema de los
    mismos. La función también identifica los cudros y las regiones dentro del
    cuadro donde faltan datos, es decir, el número de marcadores que se
    encuentra no es el esperado.
    Devuelve un arreglo que contiene todos los marcadores del segmento de video
    que se le pasa como argumento, junto a una lista de cuadros y regiones que
    deben ser interpoladas.

    :param stream: stream de video para ser analizado.
    :type stream: cv2.VideoCapture
    :param n_frames: el número de cuadros que contiene el segmento de video.
    :type n_frames: int
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    :return: arreglo con los arreglos de los centros del marcadores que se
     encontraron en el fragmento de video. Lista con los indices de los cuadros
     y las regiones de cada cuadro que contienen datos ausentes.
    :rtype: tuple
    """
    markers = []
    # Missing_regions es un diccionario con listas, donde cada clave es una
    # región del esquema, y cada lista es el índice del cuadro de video
    # en el que se perdió al menos uno de los marcadores.
    missing_regions = defaultdict(list)
    # Missing_frames es un diccionario de listas, en donde cada clave es una
    # región del esquema, y cada lista contiene listas de cuadros consecutivos,
    # donde se perdió al menos uno de los marcadores de la región.
    missing_frames = defaultdict(list)
    for i in xrange(n_frames):
        # Se lee el cuadro y se extraen los centros de los marcadores en
        # un arreglo de numpy.
        __, frame = stream.read()
        centers = np.array(map(marker_center, find_markers(frame)))[::-1]
        # Si el número de marcadores es el adecuado, entonces se almacena
        # en una variable temporal el arreglo de centros por si es
        # necesario en el siguiente cuadro rellenar un arreglo incompleto
        if len(centers) == sum(schema['schema']):
            temp = centers
            # Si existen regiones en las que se perdieron datos de marcadores
            # en al menos un cuadro de video, entonces deben agregarse al
            # diccionario que se utiliza para interpolar datos faltantes.
            if missing_regions:
                for r, v in missing_regions.iteritems():
                    missing_frames[r].append(v)
                # Se deben reiniciar las listas hasta que se pierda algún
                # marcador en un próximo cuadro de video.
                missing_regions.clear()
        else:
            # Si el arreglo está incompleto entonces se rellena el arreglo
            # en las regiones donde falten marcadores. En este proceso se
            # buscan las regiones de los marcadores en el último arreglo
            # completo.
            roi = regions(temp, schema, kwargs['ratio_scale'])
            centers, invschema = filling(centers, roi, schema)
            # Por cada región (porque puede ser mas de una) en la que
            # faltaros datos se registra el índice del cuadro en forma de
            # lista.
            for r in invschema:
                missing_regions[r].append(i)
        markers.append(centers)
    return (np.array(markers), missing_frames)


def regions(centers, schema, ratio_scale=1.0):
    u"""Encuentra los centros de las regiones del esquema.

    Los marcadores se encuentran diagramados dentro de un esquema segun
    regiones. Esta función devuelve el centro de región junto con un radio.
    Estos dos valores se utilizan para delimitar un entorno donde es posible
    encontrar los marcadores e identificarlos en un grupo cuando el esquema no
    está completo, es decir, cuando se pierden marcadores.
    El valor que devuelve como centro es el valor centro de la región en la
    coordenada "y", es decir la altura del cuadro donde se encuentra la región.
    El valor que devuelve como radio, es la distancia que existe entre los
    marcadores de los extremos de la región, multiplicada por el valor del
    argumento ratio_scale.

    :param centers: arreglo que contiene los centros de los marcadores. Este
     arreglo es de rango completo, contienen el número de marcadores que espera
     el esquema.
    :type centers: np.ndarray
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    :param ratio_scale: valor con el que se escala el radio de la región.
    :type ratio_scale: float
    :return: vectores con el centro y radio de cada una de las regiones
     diagramadas en el esquema.
    :rtype: list
    """
    regions = []
    # Se separa el arreglo de centros de marcadores según el esquema.
    for i, j in schema['slices']:
        roi = centers[i: j]
        # Se toman los valores "y" de los extremos del conjunto.
        # BUG:  Según este resultado, si el número generado por el conjunto es
        # 1, entonces no existe radio para el entorno.
        y1, y2 = roi[(0, -1), 1]
        dh = (y2 - y1)
        roi_center = y1 + dh*.5
        regions.append((roi_center, dh*ratio_scale))
    return regions


def filling(centers, roi, schema):
    u"""Esta función completa el rango del arreglo de marcadores.

    Esta función se ejecuta cuando el rango de la matriz de marcadores es menor
    que el esperado según el esquema. Se analiza el arreglo por regiones,
    cuando en alguna de ellas existe menor cantidad de datos, entonces la
    región se rellena con valores aleatorios. Los valores de las regiones donde
    el número es el correcto se mantienen.

    :param centers: el arreglo de centro de marcadores.
    :type centers: np.ndarray
    :param roi: vector con valores de centro y radio de una región para crear
     un entorno de búsqueda.
    :type roi: list
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    :return: vector cuya primera componente es el arreglo de marcadores con
     rango completo, y segunda componete una lista de esquema incompleto.
    :rtype: tuple
    """
    # Las variables que se utilizan para indexar el arreglo de centros
    # marcadores. La variable k es secundaria a j, y se adapta a cuando existe
    # una región donde faltan datos.
    j, k = 0, 0
    # La variable replace es una lista que contiene el índice de la región del
    # vector esquema al que le faltan datos.
    replace = []
    # El nuevo arreglo "vacio" que se devuelve para interpolar. Los espacios
    # que que no son ocupados por la región orignal es basura, no fiarse de
    # esos valores. La variable i representa al índice de la región en el
    # esquema.
    resized_centers = np.empty((sum(schema['schema']), 2), dtype=int)
    for i, ((c, r), s) in enumerate(zip(roi, schema['schema'])):
        # En el arreglo rmark están los centros de los marcadores que
        # corresponden al entorno delimitado por la región.
        upper_limit = centers[:, 1] > c-r
        lower_limit = centers[:, 1] < c+r
        rmark = centers[np.logical_and(upper_limit, lower_limit)]
        if len(rmark) != s:
            # Si el número de marcadores dentro de la región no es el esperado,
            # entonces el arreglo queda "vacio" en ese lugar y se reduce el
            # número necesario en la variable secundaria de indexación.
            replace.append(i)
            k = j - (s - len(rmark))
        else:
            # Los marcadores originales se mantienen.
            resized_centers[j: j+s] = centers[k: k+s]
        j += s
        k += s
    return (resized_centers, replace)


def sort_foot_markers(markers):
    u"""Ordena los marcadores del grupo de tobillo.

    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    :return: indicador de la realización de reordenamiento.
    :rtype: bool
    """
    temp = markers.copy()
    # Se toma la distancia entre el marcador de tobillo y retro pie.
    d0 = np.linalg.norm(markers[:, -3, :] - markers[:, -2, :], ord=1, axis=1)
    # Se toma la distancia entre el marcador de tobillo y ante pie.
    d1 = np.linalg.norm(markers[:, -3, :] - markers[:, -1, :], ord=1, axis=1)
    # Si la distancia d0 es mayor que d1, entonces find_markers ordenó los
    # marcadores de pie de forma distinta a lo que se espera según el esquema.
    swap_mask = d0 > d1
    if swap_mask.any():
        markers[swap_mask, -2, :] = temp[swap_mask, -1, :]
        markers[swap_mask, -1, :] = temp[swap_mask, -2, :]
        return True
    else:
        return False


def interpolate(markers, missing_frames, schema):
    u"""Interpolación de datos faltantes.

    Esta función interpola en el arreglo de centros de marcadores, nuevos
    valores aproximados (lineal) en las regiones y cuadros donde no se pudieron
    leer los marcadores.
    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param missing_frames: diccionario que contiene por regiones las listas de
     índices de cuadro en los que faltan datos.
    :type missing_frames: dict
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    """
    # missing_frames es un diccionario que tiene como clave la región en la que
    # se deben interpolar los datos, y como valor una lista de intervalos de
    # cuadros en los que existen datos faltantes para esa región.
    for reg, missing in missing_frames.iteritems():
        if not missing:
            continue
        # Por cada región se trabaja sobre la lista de datos faltantes, y se
        # generan los extremos (xp) de cada intervalo en missing. Estos
        # f(xp) = fp{x/y} son valores de reales del arreglo de centros.
        mis = reduce(lambda x, y: x+y, missing)
        xp = reduce(lambda x, y: x+y, [(m[0]-1, m[-1]+1) for m in missing])
        for i in xrange(*schema['slices'][reg]):
            # aquí se calculan por vez los valores "x", y los valores "y". Los
            # "fpx" y "fpy" son los valores que se presentan en "x" y en y en
            # los puntos "xp" que son los valores referencia de la
            # interpolación.
            markers[mis, i, 0] = np.interp(mis, xp, markers[xp, i, 0])
            markers[mis, i, 1] = np.interp(mis, xp, markers[xp, i, 1])


def gait_cycler(markers, schema, cy_markers=("M5", "M6"), ph_threshold=2.5):
    u"""Busca si existen ciclos de apoyo y balanceo en la caminata.

    La función busca si existen ciclos de marcha, apoyo y balanceo, dentro
    de la caminata. Utiliza los centros de los marcadores del pie a través
    del cambio de velocidad de dichos marcadores.
    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param schema: esquema de marcadores diagramado.
    :type schema: dict
    :param cy_markers: son los índice de fila (marcadores) en los que se
     tiene que tomar la velocidad. Por defecto son los últimos dos, que se
     corresponden con los del pié según el diagrama del esquema. El vector
     cy_markers siempre tiene que ser de dimensión 2 de otra manera se
     lanzará una exepción. Los argumentos del vector pueden ser el mismo
     componente (ej: ("M5", "M5")).
    :type cy_markers: tuple
    :param ph_threshold: Es el umbral que se toma para separar el apoyo del
     balanceo.
    :type ph_threshold: float
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
    ix = [k for k, m in enumerate(schema['codes']) if m in cy_markers]
    if len(ix) == 1:
        ix += ix
    # La media de la derivada de posicion en x e y de los marcadores de retro
    # (-2) y ante pie (-1). El valor absoluto es porque solo estoy interesado
    # en cuando toma valor cero o distinto de cero.
    diff = np.abs(np.gradient(markers[:, ix, :], axis=0).mean(axis=2))
    mov = np.logical_and(*(diff >= ph_threshold).transpose())

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
            cycles.append((st[0], tf, st[1]))
            st.pop(0)
    return (diff, mov, cycles)


def direction(markers, schema):
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
    ix = [k for k, m in enumerate(schema['codes']) if m in foot]
    # El vector que representa al segmento del pié es la diferencia del
    # marcador del antepié con la del retropié.
    xrfoot, xffoot = markers[:, ix, 0].transpose()
    # La dirección es la media de las distancias en x entre el pie anterio y el
    # pie posterior. Si este número es mayor que cero, entonces avanza en
    # sentido positivo de las x y el lado que se evalua es el derecho, de otra
    # forma es izquierdo.
    return int((xffoot - xrfoot).mean(axis=0) > 0)


@contextmanager
def open_video(path):
    u"""Lectura segura del archivo.

    :param path: La ruta del archivo de video.
    :type path: str
    """
    video = cv2.VideoCapture(path)
    yield video
    video.release()


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


def expanse_sample(angles, sample):
    u"""."""
    # Se aumenta la cantidad de elemento del dominio de x.
    x = np.linspace(0, angles.shape[1], sample)
    # El dominio original del arreglo de ángulos.
    xs = np.arange(angles.shape[1])
    expanse = []
    # Por cada articulación se hace una interpolación lineal por cada elemento,
    # nuevo en el dominio de x para aumentar el tamaño de la muestra a "sample"
    for joint in angles:
        expanse.append(np.interp(x, xs, joint))
    return np.array(expanse)


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


def calculate_angles(markers, cycle, schema, direction, **kwargs):
    u"""Calculo de angulos durante el ciclo de marcha.

    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param cycle: índices de los cuadros que contienen un ciclo dentro de la
     caminata
    :type cycle: tuple
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
    istrike, __, fstrike = cycle
    dmarkers = {}
    for i, m in enumerate(schema['codes']):
        dmarkers[m] = markers[istrike: fstrike, i, :]
    # Se forman los segmentos según lo diagramado en el esquema.
    dsegments = {}
    for s, (a, b) in schema['segments'].iteritems():
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
    for j in schema['joints']:
        segments = [dsegments[i] for i in joint_functions_args[j]]
        langles.append(joint_functions[j](*segments))
    angles = np.array(langles)
    # El usuario puede elegir si quiere que los datos obtenidos sean ajustados
    # por el uso de la transformada de fourier y así suavizadas las curvas con
    # los extremos alineados.
    if kwargs['ffit']:
        return fourier_fit(angles, sample=100, fft_scope=kwargs['fft_scope'])
    # En caso de que no se elija el ajuste los ángulos se devuelven con tamaño
    # de muestra de 100 elementos.
    else:
        return expanse_sample(angles, sample=100)


def calculate_spacetemp(markers, cycle, fps):
    u"""Cálculo de los parámetros espacio temporales.

    :param markers: arreglo de conjunto de centros de marcadores.
    :type markers: np.array
    :param cycle: índices de los cuadros que contienen un ciclo dentro de la
     caminata
    :type cycle: tuple
    :param fps: cuadros por segundos.
    :type fps: float
    :return: parámetros espacio-temporales: (duracion ciclo, fase de apoyo,
     fase de balanceo, cadencia, zancada, velocidad media).
    :rtype: tuple
    """
    # la duración en segundos,
    istrike, swing, fstrike = cycle
    # Se calcula la duración en cuadros
    framesduration = float(fstrike - istrike)
    # la duración en segundos.
    duration = framesduration / fps
    # la longitud de zancada.
    stride = np.linalg.norm(markers[(0, -1), -2, :], ord=1)
    # Se adjuntan las unidades de cada parámetro.
    # NOTE: Hasta que no se haga la calibración de la imagen y la conversión de
    # unidades, las distancias van a estar en pixeles.
    return (
        (duration, '[s]'),
        ((swing - istrike) / framesduration, '[%]'),
        ((fstrike - swing) / framesduration, '[%]'),
        (120 / duration, '[steps/min]'),
        (stride, '[px]'),
        (stride / duration, '[px/s]')
    )


class KinematicsEngine(object):
    u"""Motor de extracción y procesamiento de datos de marcha humana.

    :param files: vector que contiene las rutas de los archivos con datos de
     marcha, ya sean de video o exportaciones desde Kinovea.
    :type files: tuple
    :param config: API de configuracion.
    :type config: configparser.ConfigParser
    """

    def __init__(self, files, config):
        self.user = {}
        self.files = files
        self.config = config
        self.main_data = deque(maxlen=100)
        self.validation_data = deque(maxlen=100)
        # Desde acá se encuntran las colecciones que se utilizan cuando se le
        # ordena al motor ejecutarse en modo debug.
        self.original_markers = deque(maxlen=100)
        self.boolean_sorted_markers = deque(maxlen=100)

    def set_config(self):
        u"""Configuración del motor con valores de usuario."""
        # Se abre el archivo json de esquemas.
        with open(self.config.get('engine', 'schema')) as fh:
            self.schema = json.load(fh)
        # Se setea el modo de ejecución.
        self.mode = self.config.get('engine', 'mode')
        # Valores de control de proceso por parte del usuario.
        # Vectores:
        for k in ('cy_markers',):
            self.user[k] = self.config.get('engine', k).split('-')
        # Flotantes:
        for k in ('image_threshold', 'ph_threshold', 'ratio_scale'):
            self.user[k] = self.config.getfloat('engine', k)
        # Enteros:
        for k in ('fft_scope',):
            self.user[k] = self.config.getint('engine', k)
        # Boleanos:
        for k in ('ffit',):
            self.user[k] = self.config.getboolean('engine', k)

    def run(self):
        u"""Inicia el motor de búsqueda de parametros de marcha."""
        # Antes de comenzar la exploración de los archivos se realiza la
        # configuración de los parámetros que establece el usuario.
        self.set_config()

        for f in self.files:
            ext = os.path.basename(f).split('.')[-1]
            if ext in ('avi', 'mp4'):
                self.video_explorer(f, **self.user)
            elif ext in ('txt',):
                self.kinovea_explorer(f)
            else:
                raise Exception(u"MasMarcha: Formato de archivo NO soportado")

    def video_explorer(self, videofile, **kwargs):
        u""".

        """
        # La función de find_walks reccorre todo el video en búsqueda de
        # caminatas que cumplan la condicion de tener los extremos de esquema
        # completo. Es la función que mas afecta en el tiempo de ejecución del
        # motor de lectura cuando se ejecuta sobre un video.
        self.find_walks(videofile)
        n = len(self.main_data)
        # La función explore_walk modifica las listas principal y de validacion
        # del motor.
        while n:
            self.explore_walk(videofile, 'W%d' % n, **kwargs)
            n -= 1

    def kinovea_explorer(self, textfile):
        u""".

        :param schema: esquema de marcadores diagramado.
        :type schema: dict
        """
        return NotImplemented

    def explore_walk(self, source, wid, **kwargs):
        u""".
        :param source: dirección del archivo de video.
        :type source: str
        """
        start, end = self.main_data.pop()
        with open_video(source) as stream:
            # Se situa el video en el cuadro en el que empieza la caminata.
            stream.set(cv2.CAP_PROP_POS_FRAMES, start)
            # De cada cuadro de video se extraen arreglos con los centros
            # de los marcadores, ordenados por fila según el diagrama de
            # esquemas. Al mismo tiempo se genera una lista de los cuadros
            # y regiones en los que faltan datos.
            markers, missing = identifying_markers(
                stream, end-start, self.schema, **kwargs
            )
        if self.mode == 'debug':
            self.original_markers.appendleft(markers.copy())
        # Se revisa el orden dentro de los marcadores de la región del pie,
        # puesto que en la lectura hecha por OpenCV puede haberse invertido el
        # orden de los marcadores de pie. El valor de retorno es boleano.
        ret = sort_foot_markers(markers)
        # Si el modo de ejecución es debug, entonces se agregan a la cola
        # boolean_sorted_markers valores boleanos que indican si los marcadores
        # fueron ordenados o no.
        if self.mode == 'debug':
            self.boolean_sorted_markers.appendleft(ret)
        # Se completan los arreglos de centros de datos con valores
        # interpolados con método lineal.
        interpolate(markers, missing, self.schema)
        # Se obtienen los ciclos dentro de la caminata, y dos arreglos mas que
        # se utilizan para mostrar las velocidades y los cambios de fase.
        diff, mov, cycles = gait_cycler(
            markers, self.schema, kwargs['cy_markers'], kwargs['ph_threshold']
        )
        # Si no se encontraron ciclos en los marcadores, y el modo de ejecución
        # es "regular", entonces finaliza la exploración y no se agregan
        # valores a las listas de datos primaria y secundarios.
        if not cycles and self.mode == 'regular':
            return
        # Si existen ciclos o el modo de ejecución es "debug", se agregan los
        # valores hallados a los datos.
        # Los datos que se utilizan en el cálculo de parámetros se almacenan
        # en la cola principal.
        self.main_data.appendleft((wid, markers, cycles))
        # Los datos que se utilizan para mostrar el proceso de los ciclos y las
        # estadisticas de procesado de marcadores  se almacenan en la cola
        # de validación.
        self.validation_data.appendleft((wid, missing, diff, mov))

    def find_walks(self, source):
        u"""Separa en caminatas el archivo.

        Cada caminata tiene como extremos cuadros que contienen exactamente
        el número de marcadores esperados, esto es para que en caso de tener
        que realizar una interpolación de datos, se encuentre el número total
        de marcadores.

        :param source: dirección del archivo de video.
        :type source: str
        """
        walking = False
        first, backward, i = 0, 0, 0
        N = sum(self.schema['schema'])
        with open_video(source) as stream:
            # Se toma el valor de cuadros por segundos para el cálculo de
            # parámetros espaciotemporales.
            self.fps = stream.get(cv2.CAP_PROP_FPS)
            ret, frame = stream.read()
            while ret:
                n = len(find_markers(frame))
                # Si el número de marcadores es cero, es porque todavia
                # no comenzó la caminata o acaba de terminar.
                if n == 0:
                    # Si se encuentra dentro de la caminata, entonces un
                    # índice cero señala el fin de la misma.
                    if walking:
                        last = i - backward
                        self.main_data.append((first, last))
                        walking = False
                else:
                    # Si el número de marcadores es distinto de cero e
                    # igual al número de marcadores, y la caminata aún
                    # no empieza, entonces este es el primer cuadro que
                    # se toma como activo.
                    if n == N:
                        if not walking:
                            first = i
                            walking = True
                        else:
                            backward = 0
                    # Si no es el número esperado de marcadores entonces
                    # puede suceder que los marcadores aún no consigan el
                    # número esperado para iniciar la caminata, que estando
                    # inciada, se pierdan marcadores en la lectura (ej.
                    # ocultamiento) o que la caminata esté llegando a su fin.
                    # En este último caso se debe recordar los últimos r
                    # ciclos para volver al cuadro donde fueron hallados
                    # el número correcto de marcadores.
                    else:
                        backward += 1
                ret, frame = stream.read()
                i += 1

    def calculate_params(self):
        u"""Calcula los parámetros de marcha."""
        self.parameters = []
        # Para el cáculo de parámetros se utilizan los datos que se encuentran
        # en la lista principal.
        # Cada elemento dentro de la lista es un vector de tres componentes, la
        # identificación de la caminata, el arreglo de centros de marcadores
        # de la caminata y el conjunto de índices de cyclos, si es que se
        # encontró alguno.
        for data in self.main_data:
            wid, markers, cycles = data
            # Si existen ciclos, por cada uno se calculan los ángulos de las
            # articulaciones definidas por el esquema, y los parámetros espacio
            # temporales.
            dire = direction(markers, self.schema)
            for i, cycle in enumerate(cycles):
                # En la lista de parámetros encontrada por el motor, se ordenan
                # vectores con los componentes: identidad del ciclo, arreglo
                # de ángulos, y diccionario con parámetros espaciotemporales.
                cid = '{d}{w}C{i}'.format(d=('I', 'D')[dire], w=wid, i=i+1)
                angles = calculate_angles(
                    markers, cycle, self.schema, dire, **self.user
                )
                stemp = calculate_spacetemp(markers, cycle, self.fps)
                self.parameters.append((cid, angles, stemp))


if __name__ == '__main__':
    import configparser
    import io
    from time import time

    cfile = io.BytesIO("""
    [engine]
    mode = regular
    schema = /home/mariano/Devel/masmarcha/src/defaultschemas/schema-7.json
    image_threshold = 240.0
    ratio_scale = 1.0
    ph_threshold = 2.5
    cy_markers = M5-M6
    fft_scope = 4
    ffit = True
    """)

    path = '/home/mariano/Descargas/VID_20170720_132629833.mp4'  # Belen

    config = configparser.ConfigParser()
    config.read_file(cfile)

    t1 = time()
    E = KinematicsEngine((path, ), config)
    E.run()
    print ('Tiempo de ejecución: {}'.format(time() - t1))
