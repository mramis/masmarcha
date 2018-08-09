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


from collections import defaultdict
from contextlib import contextmanager
import json
import logging
from time import sleep

import cv2
import numpy as np


@contextmanager
def open_video(filepath):
    video = cv2.VideoCapture(filepath)
    yield video
    video.release()
    cv2.destroyAllWindows()


def get_fps(filepath):
    with open_video(filepath) as video:
        return video.get(cv2.CAP_PROP_FPS)


def find_contours(frame, threshold=250.0, dilate=False):
    u"""Encuentra dentro del cuadro los contornos de los marcadores.
    """
    # Se pasa el cuadro a canal de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Se binariza la imagen gris, el umbral puede ser modificado por el usuario
    binary = cv2.threshold(gray, threshold, 255., cv2.THRESH_BINARY)[1]
    if dilate:
        # Se puede aplicar la opción de dilatar la imagen si es necesario
        # corregir las opciones de algunos brillos muy cercanos a los
        # marcadores. Se establece un número máximo de iteraciones
        # en la dilatacion.
        binary = cv2.dilate(binary, np.ones((5, 5), np.uint8), iterations=3)
    # se devuelven los contornos de los marcadores en la imagen binarizada.
    return cv2.findContours(binary,
                            cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[1]


def contour_center(contour):
    u"""Devuelve los centros de los contorno del marcador."""
    x, y, w, h = cv2.boundingRect(contour)
    return x + w/2, y + h/2


def contour_centers_array(contours):
    u"""Obtiene los centros de los contornos como un arreglo de numpy.
    """
    list_of_contour_centers = [contour_center(c) for c in contours]
    # el arreglo se devuelve ordenado de menor a mayor en "y-es" porque así es
    # como se genera la lectura del cuadro en opencv. Cada fila del arreglo
    # contien el centro (x, y) del contorno detectado.
    return np.array(list_of_contour_centers, dtype=int)[::-1]


def find_walks(filepath, schema):
    u"""Encuentra las caminatas dentro de un video.
    """
    # Se establecen parámetros para el control del flujo de datos.
    index_frame, back_frames, first_wframe, walking = 0, 0, 0, False
    N = sum(schema['schema'])
    markers_contours = []
    # Se comienza con la búsqueda de caminatas. Cada caminata se concibe
    # como un conjunto de cuadros consecutivos, en los que el primer y
    # último cuadro presentan el esquema completo de marcadores.
    with open_video(filepath) as video:
        ret, frame = video.read()
        while ret:
            contours = find_contours(frame)
            n = len(contours)
            # Si el número de marcadores es cero, es porque todavia
            # no comenzó la caminata o acaba de terminar.
            if n == 0:
                # Si se encuentra dentro de la caminata, entonces un
                # índice cero señala el fin de la misma.
                if walking:
                    # se retroceden los últimos cuadros en los que no se
                    # obtuvo el esquema completo de marcadores.
                    walk_between = (first_wframe, index_frame - back_frames)
                    yield (walk_between, markers_contours[:-back_frames])
                    # Ya no hay marcadores en la escena y esta parte del
                    # código no se volverá a ejecutar hasta que comience
                    # una nueva caminata.
                    markers_contours.clear()
                    walking = False
            else:
                # Si el número de marcadores es se corresponde con el
                # esquema completo y además, es la primera vez que sucede,
                # entonces comienza la caminata de esquema completo.
                if n == N:
                    if not walking:
                        first_wframe = index_frame
                        walking = True
                    # De otra manera la caminata se encuentra en curso y se
                    # tiene la posibilidad de que este cuadro sea el último
                    # de esquema completo
                    else:
                        back_frames = 0
                # Si no es el número esperado de marcadores entonces puede
                # suceder que los marcadores aún no consigan el número esperado
                # para iniciar la caminata, que estando inciada, se pierdan
                # marcadores en la lectura (ej. ocultamiento) o que la caminata
                # esté llegando a su fin.
                # En este último caso se debe recordar los últimos r cuadros
                # para volver al índice de cuadro donde fueron hallados el
                # número correcto de marcadores.
                else:
                    back_frames += 1
                # Si existen marcadores entonces se agregan a la lista para
                # para entregarse en el punto de corte (yield).
                if walking:
                    markers_contours.append(contours)
            ret, frame = video.read()
            index_frame += 1


def explore_walk(walk, schema, extrapx):
    u"""."""
    # Este diccionario contiene los cuadros perdidos (que no contienen toda la
    # información) separado por regiones de interes. Este diccionario es
    # modificado por la función filling_missing_schema, que es la que rellena
    # el arreglo de centros cuando existe un número menor detectado.
    missing_frames = defaultdict(list)
    # markers es la lista que recibe los centros de los contornos cuando el
    # esquema se encuentra completo, que, a menos que se trate de contaminación
    # son los marcadores que se colocan sobre la persona.
    markers = []
    # lost es la lista que contiene aquellos centros que no completaron esquema
    # esta se utiliza en la función que completa el arreglo de centros.
    lost = []
    # regions es una lista que contiene las regiones de interes donde se
    # encuentran o deberian encontrarse los marcadores. Esta lista se almacena
    # completa para poder dibujarla en el video en caso de querer revisar los
    # ROIS.
    regions = []
    # Los extremos de posición en indices de cuadros del video en la que se
    # halló la caminata.
    cur_walk_video_frame_index, last_walk_video_frame_index = walk[0]
    # Comienza la extracción de centros de cada uno de los contornos que fueron
    # hallados en la caminata.
    for contours_array in walk[1]:
        centers = contour_centers_array(contours_array)
        if centers.shape[0] == sum(schema['schema']):
            # cada vez que el esquema está completo tienen que calcularse las
            # regiones de interes (ROI) y agregarse a la lista de regiones.
            # En este punto el sistema tiene una fragilidad, no puede
            # etiquetar correctamente a los contornos, supone que no existe
            # contaminación visual y entonces cada uno de los contornos es un
            # marcador.
            cur_regions = get_regions(cur_walk_video_frame_index, centers,
                                      schema, extrapx)
            if lost:
                # Si existen cuadros perdidos o incompletos, entonces se tienen
                # se tienen que generar las regiones de interés que no pudieron
                # ser calculadas asi que se interpolan los componentes de las
                # mismas en la siguiente función.
                iregions = interpolate_lost_regions((regions[-1], cur_regions),
                                                     schema)
                # una vez que se tienen las rois (interpoladas), se obtienen
                # nuevos arreglos de centros que quiene la misma dimensión que
                # los de esquema completo, y se rellenan con datos originales
                # de lectura que provienen de la lista lost, y de datos
                # "vacios" que posteriormente son interpolados para obtener
                # aprocimaciones lineales.
                # Esta función toma la  lista de cuadros perdidos para
                # agregarles estos datos.
                try:
                    fmarkers = filling_missing_schema(lost, iregions,
                                                      missing_frames,
                                                      schema)
                except Exception:
                    return None
                # Se inicializa la lista de cuadros de esquma incompleto.
                lost.clear()
                # Se agrega a la lista marcadores el centro actual, para
                # tenerlo ordenado con los que se completaron prescedentemente.
                markers.extend(fmarkers)
                markers.append(centers)

                regions.extend(iregions)
                regions.append(cur_regions)

            else:
                markers.append(centers)
                regions.append(cur_regions)

        else:
            # Si no se cumplió con el esquema, entonces el arreglo de centros
            # tiene un número menor de marcadores, y tiene que aumentarse el
            # tamaño del mismo y rellenar, si se puede con los datos en los que
            # tiene seguridad (a través de los ROI) que se corresponden con los
            # marcadores.
            # Se agregan los datos obtenidos a la lista lost, estos se utilizan
            # para completar la lista markers luego de ser rellenados.
            lost.append(centers)
        # aumenta en cada bucle el índice relativo al video.
        cur_walk_video_frame_index += 1
    if markers:
        markers = np.array(markers)
        # se ordenan los marcadores del pie, que pueden haberse intercambiado
        # en la lectura.
        sort_foot_markers(markers)
        # se hace una interpolación lineal de las componentes del vector de
        # posición de cada uno de los marcadores que no se entoctró en el
        # cuadro (missing_frames).
        interpolate_lost_frames(markers, missing_frames, schema, walk[0][0])
        return(np.arange(*walk[0]), markers, regions)


def get_regions(frame_index, centers, schema, extrapx):
    u"""Arreglos de vértices coordenados de una regione en la imagen.

    Las regiones de interés son arreglos Nx2x2 (N definida en el
    esquema). Cada fila de subarreglo 2X2 tiene como filas las cordenadas de
    los puntos extremos P0, P1 de un rectángulo en la imagen.
    :param centers: arreglo de marcadores de rango completo.
    :type centers: np.ndarray
    :param schema: esquema de marcadores definido por el usuario.
    :type schema: dict
    :param px: inremento en pixeles de los límites de la region encontrada.
    :param px: int
    """
    regions = []
    # Se separa el arreglo de centros de marcadores según el esquema.
    for i, j in schema['slices']:
        # NOTE: quizás px tenga que ser proporcional, a la resolución del vid.
        regions.append(
            np.array((np.min(centers[i: j], axis=0) - extrapx,
                      np.max(centers[i: j], axis=0) + extrapx)))
    return np.hstack((frame_index, np.array(regions).flatten()))


def interpolate_lost_regions(regions, schema):
        u"""."""
        # NOTE: hay que reformar el codigo para aceptar la nueva disposición.

        # prev y cur son las regiones (arreglos) extremas de una sucesión de
        # regiones sin datos, y son estas regiones las que aportan los datos
        # para la interpolación.

        pre, cur = regions
        dom = np.arange(pre[0] + 1, cur[0])

        empty = np.empty((dom.size, len(schema['schema'])*2*2))
        for i in range(pre[1:].size):
            empty[:, i] = np.interp(dom, (pre[0], cur[0]), (pre[i+1], cur[i+1]))

        return(np.hstack((dom.reshape(dom.size, 1), empty)))

        # NOTE: OLD
        # # El primer valor del arreglo de regiones es el índice del cuadro al
        # # que pertenecen.
        # (jf, jroi), (kf, kroi) = regions
        # # arreglo de índices, es el dominio (x) de la función de interpolación,
        # # cuyo resultado es f(x).
        # xindex = np.arange(prev[0] + 1, cur[0])
        # # los valores que tienen los índices en los extremos, es uno de los
        # # datos conocidos que requiere la función.
        # xends = (prev[0], cur[0])
        # # los valores que tienen los puntos en esos índices extremos.
        # yends = np.array((jroi, kroi))
        # # El arreglo que tiene la forma que se necesita, y que después va a
        # # se completada con los valores interpolados.
        # yrois = np.empty((len(xindex), len(schema['schema']), 2, 2))
        # for i in range(len(schema['schema'])):
        #     # Se interpolan las coordenadas de las esquinas, superior izquierda
        #     # P0 = x0, y0, y la esquina inferior derecha P1 = x1, y1, para cada
        #     # uno de los cuadros en los que se perdieron (o sobran) marcadores.
        #     yrois[:, i, 0, 0] = np.interp(xindex, xends, yends[:, i, 0, 0])
        #     yrois[:, i, 1, 0] = np.interp(xindex, xends, yends[:, i, 1, 0])
        #     yrois[:, i, 0, 1] = np.interp(xindex, xends, yends[:, i, 0, 1])
        #     yrois[:, i, 1, 1] = np.interp(xindex, xends, yends[:, i, 1, 1])
        #
        # return[(index, list(rois)) for index, rois in zip(xindex, yrois)]


def filling_missing_schema(lost, iregions, missing_frames, schema):
    u""".

    :param lost: Conjunto de cuadros de esquema incompleto.
    :type lost: list
    :param iregions: Conjunto de regions interpoladas.
    :type iregions: numpy.ndarray
    """
    # Se construye un arreglo de cuatro dimensiones(FxSx2), donde F es la
    # cantidad de cuadros de video en los que el esquema no estuvo completo,
    # son los cuadros de la lista "lost"; S es la cantidad de marcadores que
    # se definen en el esquema; y 2 es la cantidad de componentes que tiene
    # cada vector de posición del marcador (x, y).
    schema_centers = np.empty((len(lost), sum(schema['schema']), 2), dtype=int)
    for i, (centers, regions) in enumerate(zip(lost, iregions)):
        # NOTE: MODIFICADO
        frame_index = int(regions[0])
        rois = regions[1:].reshape(len(schema['schema']), 2, 2)
        # rep es un índice que se utiliza para indexar el arreglo de centros
        # schema_centers y reemplazar los datos aleatorios con los encontrados
        # en el correspondiente arreglo de lost.
        # org tiene el mismo fin pero se utiliza en el arreglo de centros
        # originales lost[i] = centers, estos dos índices no cambian de la
        # misma forma.
        rep, org = 0, 0
        # a continuación se buscan los marcadores por cada región en cada uno
        # de los cuadros.
        for reg, s in enumerate(schema['schema']):
            # rois tiene un arreglo por cada region, y cada arreglo tiene por
            # fila las esquinas opuestas de una region de interés. En esta
            # roi se buscan los maracadores. P0 es la esquina superior-
            # izquierda P1 la inferior-derecha.
            p0, p1 = rois[reg]
            xlower_bound = centers[:, 0] > p0[0]
            yupper_bound = centers[:, 1] > p0[1]
            xupper_bound = centers[:, 0] < p1[0]
            ylower_bound = centers[:, 1] < p1[1]
            x_ends = np.logical_and(xlower_bound, xupper_bound)
            y_ends = np.logical_and(yupper_bound, ylower_bound)
            # rmark es el arreglo que cumplen con las condiciones de region,
            # por lo tanto se hace la suposición de que son los marcadores
            # que se buscan.
            rmark = centers[np.logical_and(x_ends, y_ends)]
            if rmark.shape[0] == s:
                # Si conincide el número de marcadores de rmark con el esperado
                # por el esquema, entonces se asume que son los marcadores
                # correctos. Pero, puede suceder que haya habido un problema
                # con la generación de rois, a causa de contaminación por los
                # marcadores activos, o por superficies reflectivas en la
                # escena. entonces la sección de reemplazo se enmarca en una
                # sentencia try-except.
                try:
                    schema_centers[i,  rep: rep+s] = centers[org: org+s]
                # si el except se lanza dentro de este bucle, entonces es
                # porque hubo un problema con los rois.
                except ValueError:
                    # Si esto sucede entonces no es confiable la extracción de
                    # datos, y debe, por lo tanto descartarse la caminata.
                    logging.error("filling_missing_schema: markers-shape")
                    raise Exception
            else:
                # si no se encontraron los marcadores que se esperan en la
                # región entonces se hace la suposición de que no existen y
                # tienen que ser interpolados.
                missing_frames[reg].append(frame_index)
            # se modifican los índices que se utilizan en la indexación de los
            #  arreglos.
            rep += s
            org += rmark.shape[0]
    return(list(schema_centers))


def sort_foot_markers(markers):
    u"""Ordena los marcadores del grupo de tobillo.
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


def get_ends(missing_frames_list):
    # en la lista missing_frames_list estan los índices de los cuadros que se
    # tienen que interpolar. Estos cuadros pueden sucecederse o no. Lo que se
    # busca es encontrar los extremos de los cuadros que sean consecutivos
    # dentro de la lista.
    # Puede suceder que la lísta contenga un solo elemento, por lo tanto se
    #  escriben las siguientes do líneas.
    if len(missing_frames_list) == 1:
        return(np.array((missing_frames_list[0]-1, missing_frames_list[0]+1)))
    else:
        ends = []
        # first es una bandera que indica cuál es el primero de los extremos.
        first = None
        for i, j in zip(missing_frames_list[:-1], missing_frames_list[1:]):
            if first is None:
                first = i-1
            # esta es la condición que se cumple cuando se interrumpe la
            # continuidad.
            if i+1 != j:
                ends.extend((first, i+1))
                first = None
        # Puede que en la última iteración i y j sean discontinuos, entonces,
        # la lista se extendió y con i+1 y first se establecio vacio; pero j
        #  es un valor que no se consideró. para salvar esta perdida se agregan
        #  las siguientes líneas.
        if first is None:
            first = j-1
        ends.extend((first, j+1))
        return np.unique(ends)


def interpolate_lost_frames(markers, missing_frames, schema, first_frame_index):
    u"""Interpolación de datos faltantes.
    """
    # missing_frames es un diccionario que tiene como clave la región en la que
    # se deben interpolar los datos, y como valor una lista de intervalos de
    # cuadros en los que existen datos faltantes para esa región.
    for reg, missing in missing_frames.items():
        if not missing:
            continue
        # Por cada región se trabaja sobre la lista de datos faltantes, y se
        # generan los extremos (xp) de cada intervalo en missing. Estos
        # f(xp) = fp{x/y} son valores de reales del arreglo de centros.
        xp = get_ends(missing) - first_frame_index
        missing = np.array(missing) - first_frame_index
        for i in range(*schema['slices'][reg]):
            # aquí se calculan por vez los valores "x", y los valores "y". Los
            # "fpx" y "fpy" son los valores que se presentan en "x" y en y en
            # los puntos "xp" que son los valores referencia de la
            # interpolación.
            markers[missing, i, 0] = np.interp(missing, xp, markers[xp, i, 0])
            markers[missing, i, 1] = np.interp(missing, xp, markers[xp, i, 1])


def play(filepath, pausetime, dfunction, ends=(), size=(1024, 840), **kwargs):
    with open_video(filepath) as video:

        if ends:
            video.set(cv2.CAP_PROP_POS_FRAMES, ends[0])

        ret, frame = video.read()
        cv2.namedWindow(filepath, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(filepath, *size)

        i = 0
        while ret:
            if isinstance(ends, np.ndarray) and (ends[-1] - ends[0]) == i:
                break

            dfunction(frame, i, **kwargs)
            cv2.imshow(filepath, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            ret, frame = video.read()
            sleep(float(pausetime))
            i += 1


def draw_markers(frame, index, markers, wichone, **kwargs):
    if not isinstance(markers, np.ndarray):
        for mark in contour_centers_array(find_contours(frame)):
            cv2.circle(frame, tuple(mark), 10, (0, 0, 255), -1)
    else:
        if wichone is -1:
            for mark in markers[index]:
                cv2.circle(frame, tuple(mark), 10, (0, 0, 255), -1)
        else:
            cv2.circle(
                frame, tuple(markers[index, wichone]), 10, (0, 0, 255), -1)


def draw_rois(frame, index, regions, schema, **kwargs):
    if not regions:
        markers = contour_centers_array(find_contours(frame))
        if markers.shape[0] == sum(schema['schema']):
            rois = get_regions(0, markers, schema, kwargs['extrapx'])
            rois = rois[1:].reshape(len(schema['schema']), 2, 2)
            for p0, p1 in rois:
                cv2.rectangle(frame, tuple(np.int16(p0)),
                              tuple(np.int16(p1)), (0, 0, 255), 3)
    else:
        for p0, p1 in regions[index][1]:
            cv2.rectangle(frame, tuple(np.int16(p0)),
                          tuple(np.int16(p1)), (0, 0, 255), 3)
