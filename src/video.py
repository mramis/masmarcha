#!/usr/bin/env python3
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


import json
import logging
from time import sleep
from collections import defaultdict
from contextlib import contextmanager

import cv2
import numpy as np


@contextmanager
def open_video(filepath):
    video = cv2.VideoCapture(filepath)
    yield video
    video.release()
    cv2.destroyAllWindows()


def find_contours(frame, image_threshold=240.0):
    u"""Encuentra dentro del cuadro los contornos de los marcadores.

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


def get_markers(frame):
    u"""Los centros de los marcadores que se encuentran en el cuadro.

    :param frame: cuadro de video.
    :type frame: cv2.read (´numpy.array´)
    :return: arreglo de centros de marcadores de dos dimensiones.
    :rtype: numpy.array(dtype=int)
    """
    list_of_marker_centers = [marker_center(m) for m in find_contours(frame)]
    return np.array(list_of_marker_centers, dtype=int)[::-1]  # top/down


def find_walks(filepath, config):
    u"""Encuentra las caminatas dentro de un video.

    Cada caminata se define como un intervalo de cuadros de videos, en donde:
    - el primer y último-1 cuadro tienen esquema completo, es decir el número
    de marcadores en el cuadro es igual al número de marcadores de diseño.
    - dentro del intervalo no existe ningún cuadro con número de marcadores
    igual a 0 (cero). Esto supone que ya no existen marcadores en la escena, es
    decir que la persona no se encuentra dentro de la toma.
    La función es un generador que va obteniendo intervalos de esquema
    completo.
    :param filepath: ruta del archivo de video.
    :type filepath: str
    :param config: configuración de la aplicación.
    :type config: ConfigPaser
    :return: intervalo de caminata.
    :rtype: tuple
    """
    schema = json.load(open(config.get('engine', 'schema')))
    log = "Se hallo caminata #{} de extremos {}-{}"
    # Se establecen parámetros para el control del flujo de datos.
    index_frame, back_frames, first_wframe, walkid, walking = 0, 0, 0, 0, False
    N = sum(schema['schema'])
    # Se comienza con la búsqueda de caminatas. Cada caminata se concibe
    # como un conjunto de cuadros consecutivos, en los que el primer y
    # último cuadro presentan el esquema completo de marcadores.
    with open_video(filepath) as video:
        ret, frame = video.read()
        while ret:
            n = len(find_contours(frame))
            # Si el número de marcadores es cero, es porque todavia
            # no comenzó la caminata o acaba de terminar.
            if n == 0:
                # Si se encuentra dentro de la caminata, entonces un
                # índice cero señala el fin de la misma.
                if walking:
                    # se retroceden los últimos cuadros en los que no se
                    # obtuvo el esquema completo de marcadores.
                    walk_between = (first_wframe, index_frame - back_frames)
                    logging.info(log.format(walkid, *walk_between))
                    yield walk_between
                    # Ya no hay marcadores en la escena y esta parte del
                    # código no se volverá a ejecutar hasta que comience
                    # una nueva caminata.
                    walking = False
                    # Se establece el código de la caminata.
                    walkid += 1
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
            ret, frame = video.read()
            index_frame += 1


def get_regions(centers, schema, px=50):
    u"""."""
    regions = []
    # Se separa el arreglo de centros de marcadores según el esquema.
    for i, j in schema['slices']:
        regions.append(
            np.array((np.min(centers[i: j], axis=0) - px,
                      np.max(centers[i: j], axis=0) + px)))
    return regions


def lost_regions(regions, schema):
        u"""."""
        start_region, end_region = regions[-2:]
        # La cantidad de cuadros en los que se perdió información.
        lost_findex = np.arange(start_region[0] + 1, end_region[0])
        # El arreglo de centros de region de los cuadros extremos.
        ends_findex = (start_region[0], end_region[0])
        ends_frois = np.array((start_region[1], end_region[1]))
        # Los extremos de los rois (2x2) de las regiones (schema) de los
        # cuadros en los que se perdió información.
        interp_regions = np.empty((len(lost_findex), len(schema['schema']), 2, 2))
        for i in range(len(schema['schema'])):
            # Se interpolan las coordenadas de las esquinas, superior izquierda
            # P0 = x0, y0, y la esquina inferior derecha P1 = x1, y1, para cada
            # uno de los cuadros en los que se perdieron (o sobran) marcadores.
            interp_regions[:, i, 0, 0] = np.interp(
                lost_findex, ends_findex, ends_frois[:, i, 0, 0])
            interp_regions[:, i, 1, 0] = np.interp(
                lost_findex, ends_findex, ends_frois[:, i, 1, 0])
            interp_regions[:, i, 0, 1] = np.interp(
                lost_findex, ends_findex, ends_frois[:, i, 0, 1])
            interp_regions[:, i, 1, 1] = np.interp(
                lost_findex, ends_findex, ends_frois[:, i, 1, 1])

        return[(findex, list(rois))
               for findex, rois
               in zip(lost_findex, interp_regions)]


def filling(lost, regions, schema):
    to_replace = defaultdict(list)

    resized_centers = np.empty(
        (len(lost), sum(schema['schema']), 2), dtype=int)

    for i, (centers, (findex, rois)) in enumerate(zip(lost, regions)):
        rep, org = 0, 0
        for reg, s in enumerate(schema['schema']):
            p0, p1 = rois[reg]

            xlower_bound = centers[:, 0] > p0[0]
            yupper_bound = centers[:, 1] > p0[1]

            xupper_bound = centers[:, 0] < p1[0]
            ylower_bound = centers[:, 1] < p1[1]

            x_bounds = np.logical_and(xlower_bound, xupper_bound)
            y_bounds = np.logical_and(yupper_bound, ylower_bound)

            rmark = centers[np.logical_and(x_bounds, y_bounds)]

            if rmark.shape[0] == s:
                try:
                    resized_centers[i,  rep: rep+s] = centers[org: org+s]

                except ValueError as error:
                    # Esta excepción se lanza porque hubo algun problema en la
                    # definicion de las regiones.
                    logging.error(error)
                    # se tienen que agregar todos las regiones para interpolar
                    # porque el sistema no las pudo identificar.

                    for j in range(len(schema['schema'])):
                        to_replace[j].append(findex)

            else:
                to_replace[reg].append(findex)

            rep += s
            org += rmark.shape[0]

    return(resized_centers, to_replace)


def markers_from_walks(filepath, bounds, schema, region_extrapx):

    markers, lost, regions, to_interpolate = [], [], [], []
    fill = False
    iframe, ends = bounds

    with open_video(filepath) as video:
        video.set(cv2.CAP_PROP_POS_FRAMES, iframe)

        while True:
            centers = get_markers(video.read()[1])

            if centers.shape[0] == sum(schema['schema']):
                regions.append(
                    (iframe, get_regions(centers, schema, region_extrapx)))

                if fill:
                    interpolated_regions = lost_regions(regions, schema)
                    filling(lost, interpolated_regions, schema)
                    # markers += filled_markers
                    markers.append(centers)

                    popindex, poprois = regions.pop()
                    interpolated_regions.append((popindex, poprois))
                    regions += interpolated_regions

                    lost = []
                    fill = False

                else:
                    markers.append(centers)

            else:
                lost.append(centers)
                fill =  True

            iframe += 1
            if iframe == ends:
                break

# def show_markers_on_video(filepath, sleeptime=0.05):
#     u"""Reproduce el video mostrando los marcadores identificados.
#
#     Los marcadores se dibujan en círculos rojos en la posición en la que han
#     sido encontrados.
#     :param filepath: ruta del archivo de video.
#     :type filepath: str
#     :param sleeptime: tiempo de espera (pausa) en segundos entre cada cuadro.
#     :type sleeptime: float
#     """
#     def draw_markers(frame):
#         u"""Dibuja en el cuadro de video los marcadores como circulos rojos
#
#         :param frame: cuadro de video.
#         :type frame: cv2.read (´numpy.array´)
#         """
#         for mark in get_markers(frame):
#             cv2.circle(frame, tuple(mark), 10, (0, 0, 255), -1)
#
#     with open_video(filepath) as video:
#         ret, frame = video.read()
#
#         while ret:
#             draw_markers(frame)
#             cv2.namedWindow(filepath, cv2.WINDOW_NORMAL)
#             cv2.resizeWindow(filepath, 1000, 600)
#             cv2.imshow(filepath, frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#             sleep(sleeptime)
#             ret, frame = video.read()
#
#
# def show_frames_on_video(filepath, frames, sleeptime=0.05):
#     window_name = u"Cuadros"
#     with open_video(filepath) as video:
#         index = 0
#         while True:
#             if index == len(frames):
#                 index = 0
#             video.set(cv2.CAP_PROP_POS_FRAMES, frames[index])
#             cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
#             cv2.resizeWindow(window_name, 1000, 600)
#             cv2.imshow(window_name, video.read()[1])
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#             sleep(sleeptime)
#             index += 1
#         cv2.destroyAllWindows()
#
#
def show_rois_on_video(filepath, schema, sleeptime=0.05):

    def draw_rois(frame, rois):
        if not rois:
            return

        for p0, p1 in rois:
            cv2.rectangle(frame, tuple(p0), tuple(p1), (0, 0, 255), 3)

    rois = None
    with open_video(filepath) as video:
        ret, frame = video.read()
        while ret:

            markers = get_markers(frame)
            if markers.shape[0] == 7:  # NOTE: acá va la suma del esquema.
                rois = get_regions(markers, schema)
                draw_rois(frame, rois)

            cv2.namedWindow(filepath, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(filepath, 1000, 600)
            cv2.imshow(filepath, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            sleep(sleeptime)
            ret, frame = video.read()
