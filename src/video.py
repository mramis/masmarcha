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


import os
from collections import defaultdict
from contextlib import contextmanager
import json
import logging
from time import sleep

import cv2
import numpy as np



class Video(object):

    def __init__(self, filename, cfg):
        self.vid = cv2.VideoCapture(filename)
        self.source = filename
        self.cfg = cfg
        self.canread = True
        self.calibration = False
        self.walks = []

    def __del__(self):
        self.vid.release()

    def get_fps(self):
        return self.vid.get(cv2.CAP_PROP_FPS)

    def read_frame(self):
        ret, frame = self.vid.read()
        if self.calibration and ret:
            frame = self.undistort_frame(frame)
        return(ret, self.vid.get(cv2.CAP_PROP_POS_FRAMES), frame)

    def calculate_calibration_params(self):
        return(NotImplemented)

    def load_calibration_params(self):
        calibrationpath = self.cfg.get('paths', 'currentcamera')
        if os.path.isfile(calibrationpath):
            calibration_setup = dict(np.load(calibrationpath).items())
            self.mtx = calibration_setup['mtx']
            self.dist = calibration_setup['dist']
            self.newmtx = calibration_setup['newcameramtx']
            self.calibration = True

    def undistort_frame(self, frame):
        return(cv2.undistort(frame, self.mtx, self.dist, None, self.newmtx))

    def new_walk(self):
        n = len(self.walks)
        walk = Walk(n, self.source, self.cfg)
        self.walks.append(walk)
        return(walk)

    def explore(self):
        u"""Encuentra las caminatas dentro de un video."""
        self.walks = []
        schema = json.load(open(self.cfg.get('paths', 'schema')))
        n = sum(schema['schema'])
        walking = False
        while True:
            ret, pos, frame = self.read_frame()
            if not ret:
                break
            frame = Frame(pos, frame, schema, self.cfg)
            ncontours = frame.find_contours()
            if not walking:
                if ncontours == n:
                    walk = self.new_walk()
                    walk.add_frame(frame)
                    walking = True
            else:
                walk.add_frame(frame)
                if ncontours == 0:
                    walk.stop_walking()
                    walking = False


class Frame(object):

    def __init__(self, pos, frame, sch, cfg):
        self.pos = pos
        self.cfg = cfg
        self.schema = sch
        self.frame = frame
        self.contours = None

    def __repr__(self):
        return 'f.{0}'.format(self.pos)

    def find_contours(self):
        u"""Encuentra dentro del cuadro los contornos de los marcadores.

        :return: nmarkers, el número de contornos que se encontraron.
        :rtype: int
        """
        thresh = self.cfg.getfloat('video', 'thresh')
        dilate = self.cfg.getboolean('video', 'dilate')
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(gray, thresh, 255., cv2.THRESH_BINARY)[1]
        if dilate:
            kernel = np.ones((5, 5), np.uint8)
            binary = cv2.dilate(binary, kernel, iterations=3)
        contours = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        self.contours = contours
        self.nmarkers = len(contours)
        return(self.nmarkers)

    def contour_centers(self):
        u"""Obtiene los centros de los contornos como un arreglo de numpy.

        :return: arreglo de centros de los marcadores que se encontraron.
        :rtype: np.ndarray
        """
        def contour_center(contour):
            u"""Devuelve los centros de los contorno del marcador."""
            x, y, w, h = cv2.boundingRect(contour)
            return x + w/2, y + h/2
        list_of_contour_centers = [contour_center(c) for c in self.contours]
        markers = np.array(list_of_contour_centers, dtype=np.uint8)[::-1]
        self.markers = markers
        return(markers)

    def is_completed(self):
        """Informa si la el cuadro es de esquema completo.

        :return: True si encontro el cuadro contiene el número de marcadores
        que establece el esquema en uso.
        :rtype: bool
        """
        n = sum(self.schema['schema'])
        markers = self.contour_centers()
        if self.nmarkers == n:
            self.calculate_regions()
            return(True)
        else:
            return(False)

    def calculate_regions(self):
        """Encuentra las regiones de interes del esquema de marcadores.

        Utiliza el parámetro "roiextrapixel" que el usuario puede modificar
        desde la configuración.
        """
        regions = []
        extra = self.cfg.getint('video', 'roiextrapixel')
        for i, j in self.schema['slices']:
            regions.append(
                np.array((np.min(self.markers[i: j], axis=0) - extra,
                          np.max(self.markers[i: j], axis=0) + extra)))
        self.regions = np.array(regions).flatten()

    def get_basics(self):
        """Devuelve la información básica del cuadro.

        :return: pos (int), la posicion del cuadro dentro del video; frame
        (np.ndarray) el cuadro de video propiamente dicho.
        :rtype: tuple
        """
        return(self.pos, self.frame)


class Walk(object):

    def __init__(self, id, source, cfg):
        self.id = id
        self.cfg = cfg
        self.source = source
        self.frames = []

    def __repr__(self):
        return 'walk.{0}'.format(self.id)

    def add_frame(self, frame):
        """Agrega un cuadro a la caminata.

        :param frame: cuadro de video.
        :type frame: Frame
        """
        self.frames.append(frame)

    def stop_walking(self):
        """Pone fin al proceso de añadir cuadros a la caminata."""
        schema = json.load(open(self.cfg.get('paths', 'schema')))
        n = sum(schema['schema'])
        while True:
            frame = self.frames[-1]
            if frame.nmarkers != n:
                self.frames.pop()
            else:
                break

    def compact_frames(self):
        u"""Devuelve la informacion básica de los cuadros de la caminata.

        :return: pos, arreglo de posiciones (int) de los cuadros; frames,
        arreglo de los cuadros (np.ndarray) de video.
        :rtype: tuple
        """
        pos, frames = [], []
        for frame in self.frames:
            p, f = frame.get_basics()
            pos.append(p)
            frames.append(f)
        return(np.array(pos, dtype=np.uint8), np.array(frames, dtype=np.uint8))

    def dump(self):
        u"""Escribe los datos básicos de la caminata en disco.

        Los datos basicos son: wid, la id de la caminata dentro del video;
        source, la fuente de la caminata (ruta al video); posframes, los
        índices de cuadros de video; frames, los cuadros de video (np.ndarray).
        """
        walkpath = os.path.join(self.cfg.get('paths', 'session'), str(self))
        posframes, frames = self.compact_frames()
        np.savez(walkpath, posframes=posframes, frames=frames,
                 source=self.source, walkid=self.id)

    def load(self, walkpath):
        u"""Carga los datos basicos de la caminata.

        :param walkpath: ruta al archivo de caminata.
        :type walkpath: str
        """
        schema = json.load(open(self.cfg.get('paths', 'schema')))
        data = dict(np.load(walkpath).items())
        self.source = data['source']
        self.id = data['walkid']
        for pos, frame in zip(data['posframes'], data['frames']):
            frame = Frame(pos, frame, schema, self.cfg)
            frame.find_contours()
            self.frames.append(frame)

    def classify_frames(self):
        """Identifica los cuadros completos de la caminata.

        Devuelve las regiones de interes que se calcularon con éxito.
        :return: x, la lista de índices de cuadros incompletos; xp, la lista de
        índices de cuadros completos; fp, arreglo de regiones de interés por
        cuadro de video fp.shape = (xp.size, nregions*2*2).
        :rtype: tuple.
        """
        x, xp, fp = [], [], []
        for frame in self.frames:
            full_schema = frame.is_completed()
            if full_schema:
                xp.append(frame.pos)
                fp.append(frame.regions)
            else:
                x.append(frame.pos)
        return(x, xp, np.array(fp))

    def recovery_rois_frames(self):
        u"""Construye las regiones de interés en cuadros incompletos."""
        x, xp, fp = self.classify_frames()
        ncols = fp.shape[1]
        interp = np.empty((len(x), ncols), dtype=np.uint8)
        for i in range(ncols):
            interp[:, i] = np.interp(x, xp, fp[:, i])
        # A cada cuadro de la caminata se le agrega su roi interpolada.
        first_frame = self.frames[0].pos
        for i, frame_index in enumerate(x):
            relative_index = frame_index - first_frame
            self.frames[relative_index].regions = interp[i]
        self.uncompleted_frames = x


def calibrate_camera(source, dest, chessboard, rate):
    w, h = chessboard
    objp = np.zeros((w*h, 3), np.float32)
    objp[:, :2] = np.mgrid[0:w, 0:h].T.reshape(-1,2)

    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    with open_video(source) as video:
        read, frame = video.read()
        while read:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (w, h), None)
            # If found, add object points, image points (after refining them)
            if ret:
                objpoints.append(objp)
                imgpoints.append(corners)
            next = video.get(cv2.CAP_PROP_POS_FRAMES) + rate
            video.set(cv2.CAP_PROP_POS_FRAMES, next)
            read, frame = video.read()

    fw, fh = gray.shape[:2]
    __, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, gray.shape[::-1], None, None)
    newcameramtx, __ = cv2.getOptimalNewCameraMatrix(
        mtx, dist, (w,h), 0, (w,h))

    np.savez(dest, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs,
             newcameramtx=newcameramtx, source=source,
             chessboard=chessboard, rate=rate)

#
# def find_contours(frame, threshold=250.0, dilate=False):
#     u"""Encuentra dentro del cuadro los contornos de los marcadores.
#     """
#     # Se pasa el cuadro a canal de grises
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     # Se binariza la imagen gris, el umbral puede ser modificado por el usuario
#     binary = cv2.threshold(gray, threshold, 255., cv2.THRESH_BINARY)[1]
#     if dilate:
#         # Se puede aplicar la opción de dilatar la imagen si es necesario
#         # corregir las opciones de algunos brillos muy cercanos a los
#         # marcadores. Se establece un número máximo de iteraciones
#         # en la dilatacion.
#         binary = cv2.dilate(binary, np.ones((5, 5), np.uint8), iterations=3)
#     # se devuelven los contornos de los marcadores en la imagen binarizada.
#     return cv2.findContours(binary,
#                             cv2.RETR_EXTERNAL,
#                             cv2.CHAIN_APPROX_SIMPLE)[1]
#
#
# def contour_center(contour):
#     u"""Devuelve los centros de los contorno del marcador."""
#     x, y, w, h = cv2.boundingRect(contour)
#     return x + w/2, y + h/2
#
#
# def contour_centers_array(contours):
#     u"""Obtiene los centros de los contornos como un arreglo de numpy.
#     """
#     list_of_contour_centers = [contour_center(c) for c in contours]
#     # el arreglo se devuelve ordenado de menor a mayor en "y-es" porque así es
#     # como se genera la lectura del cuadro en opencv. Cada fila del arreglo
#     # contien el centro (x, y) del contorno detectado.
#     return np.array(list_of_contour_centers, dtype=int)[::-1]

def get_distance_scale(filepath, realdistance, maxiter=30):
    u"""Devuelve el factor de conversión entre pixeles y metros."""
    distance_centers = []
    count = 0
    with open_video(filepath) as video:
        ret, frame = video.read()
        while ret:
            cen = contour_centers_array(find_contours(frame))
            if len(cen) == 2:
                A, B = cen
                distance_centers.append(np.linalg.norm(A-B))
            count += 1
            if count > maxiter:
                break
            ret, frame = video.read()
    return (realdistance / np.mean(distance_centers))

#
# def find_walks(filepath, schema, calb=None):
#     u"""Encuentra las caminatas dentro de un video."""
#     # Se establecen parámetros para el control del flujo de datos.
#     index_frame, back_frames, first_wframe, walking = 0, 0, 0, False
#     N = sum(schema['schema'])
#     markers_contours = []
#     # Se comienza con la búsqueda de caminatas. Cada caminata se concibe
#     # como un conjunto de cuadros consecutivos, en los que el primer y
#     # último cuadro presentan el esquema completo de marcadores.
#     with open_video(filepath) as video:
#         ret, frame = video.read()
#         while ret:
#             if calb:
#                 frame = cv2.undistort(frame, calb['mtx'], calb['dist'],
#                                       None, calb['newcameramtx'])
#             contours = find_contours(frame)
#             n = len(contours)
#             # Si el número de marcadores es cero, es porque todavia
#             # no comenzó la caminata o acaba de terminar.
#             if n == 0:
#                 # Si se encuentra dentro de la caminata, entonces un
#                 # índice cero señala el fin de la misma.
#                 if walking:
#                     # se retroceden los últimos cuadros en los que no se
#                     # obtuvo el esquema completo de marcadores.
#                     walk_between = (first_wframe, index_frame - back_frames)
#                     yield (walk_between, markers_contours[:-back_frames])
#                     # Ya no hay marcadores en la escena y esta parte del
#                     # código no se volverá a ejecutar hasta que comience
#                     # una nueva caminata.
#                     markers_contours.clear()
#                     walking = False
#             else:
#                 # Si el número de marcadores es se corresponde con el
#                 # esquema completo y además, es la primera vez que sucede,
#                 # entonces comienza la caminata de esquema completo.
#                 if n == N:
#                     if not walking:
#                         first_wframe = index_frame
#                         walking = True
#                     # De otra manera la caminata se encuentra en curso y se
#                     # tiene la posibilidad de que este cuadro sea el último
#                     # de esquema completo
#                     else:
#                         back_frames = 0
#                 # Si no es el número esperado de marcadores entonces puede
#                 # suceder que los marcadores aún no consigan el número esperado
#                 # para iniciar la caminata, que estando inciada, se pierdan
#                 # marcadores en la lectura (ej. ocultamiento) o que la caminata
#                 # esté llegando a su fin.
#                 # En este último caso se debe recordar los últimos r cuadros
#                 # para volver al índice de cuadro donde fueron hallados el
#                 # número correcto de marcadores.
#                 else:
#                     back_frames += 1
#                 # Si existen marcadores entonces se agregan a la lista para
#                 # para entregarse en el punto de corte (yield).
#                 if walking:
#                     markers_contours.append(contours)
#             ret, frame = video.read()
#             index_frame += 1


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

#
# def get_regions(frame_index, centers, schema, extrapx):
#     u"""Arreglos de vértices coordenados de una regione en la imagen.
#
#     Las regiones de interés son arreglos Nx2x2 (N definida en el
#     esquema). Cada fila de subarreglo 2X2 tiene como filas las cordenadas de
#     los puntos extremos P0, P1 de un rectángulo en la imagen.
#     :param centers: arreglo de marcadores de rango completo.
#     :type centers: np.ndarray
#     :param schema: esquema de marcadores definido por el usuario.
#     :type schema: dict
#     :param px: inremento en pixeles de los límites de la region encontrada.
#     :param px: int
#     """
#     regions = []
#     # Se separa el arreglo de centros de marcadores según el esquema.
#     for i, j in schema['slices']:
#         # NOTE: quizás px tenga que ser proporcional, a la resolución del vid.
#         regions.append(
#             np.array((np.min(centers[i: j], axis=0) - extrapx,
#                       np.max(centers[i: j], axis=0) + extrapx)))
#     return np.hstack((frame_index, np.array(regions).flatten()))


# def interpolate_lost_regions(regions, schema):
#     u"""."""
#     pre, cur = regions
#     dom = np.arange(pre[0] + 1, cur[0])
#     empty = np.empty((dom.size, len(schema['schema'])*2*2))
#
#     for i in range(pre[1:].size):
#         empty[:, i] = np.interp(dom, (pre[0], cur[0]), (pre[i+1], cur[i+1]))
#
#     return(np.hstack((dom.reshape(dom.size, 1), empty)))


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
