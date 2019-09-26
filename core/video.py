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
import time
import threading

import cv2
import numpy as np

from .walk import Walk


FOURCC = cv2.VideoWriter_fourcc(*"XVID")


class VideoReader:  # producer

    def __init__(self, buffer, stopper, config=None):
        self.config = config
        self.buffer = buffer
        self.stopper = stopper
        self.is_opened = False

    def __del__(self):
        self.capture.release()

    @property
    def fps(self):  # Este tiene que salir de la base de datos.
        u"""Devuelve la cantidad de cuadros por segundo que tiene el video."""
        if self.is_opened:
            return int(self.capture.get(cv2.CAP_PROP_FPS))

    @property
    def posframe(self):
        u"""Devuelve la posición del cuadro a leer."""
        if self.is_opened:
            return int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))

    @posframe.setter
    def posframe(self, position):
        u"""Establece la pocisión inicial (cuadro) de lectura de video."""
        if self.is_opened:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, position)

    @property
    def numframes(self):
        """Devuelve la cantidad de cuadros del video."""
        if self.is_opened:
            return int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def open(self, source):
        """Inicializa la captura."""
        self.capture = cv2.VideoCapture(source)
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.config.set("frame", "width", str(width))
        self.config.set("frame", "height", str(height))
        self.is_opened = True

    def read(self):
        """Lee el cuadro actual de video."""
        return self.capture.read()

    def flipRead(self):
        """Lee el cuadro actual de video."""
        grab, frame = self.capture.read()
        return grab, cv2.flip(frame, 0)

    def start(self, flipped=False):
        u"""Inicia la captura en un hilo separado."""
        try:  # dispositivo
            source = self.config.getint("current", "source")
        except ValueError:  # archivo de video
            source = self.config.get("current", "source")

        readfunc = {False: self.read, True: self.flipRead}[flipped]

        self.open(source)
        threading.Thread(target=self.threadingRead, args=(readfunc,)).start()
        return self

    def threadingRead(self, read_function):
        while not self.stopper.is_set():
            ret, frame = read_function()

            if not ret:
                self.stopper.set()
                break

            self.buffer.put(frame)

        self.capture.release()


class VideoWriter:  # consumer
    final_time = None
    initial_time = None
    writed_frames = 0

    def __init__(self, buffer, stopper, config=None):
        self.config = config
        self.buffer = buffer
        self.stopper = stopper

    def __del__(self):
        self.writer.release()

    def setRealFPS(self):  # NOTE: Un estilo feo
        fps_calc = self.writed_frames / (self.final_time - self.initial_time)
        self.config.set("video", "fps_real", str(fps_calc))
        with open(self.config.get("paths", "configfile"), "w") as fh:
            self.config.write(fh)
        return fps_calc

    def open(self):
        w = self.config.getint("frame", "width")
        h = self.config.getint("frame", "height")
        filename = os.path.join(
            self.config.get("paths", "video"),
            self.config.get("video", "filename")
        )
        self.writer = cv2.VideoWriter(filename, FOURCC, 120, (w, h))

    def write(self, frame):
        self.writer.write(frame)
        self.writed_frames += 1

    def start(self):
        self.open()
        threading.Thread(target=self.threadingWrite, args=()).start()
        return self

    def threadingWrite(self):
        self.initial_time = time.time()

        while not self.stopper.is_set():
            frame = self.buffer.get()
            self.write(frame)

        self.final_time = time.time()
        self.setRealFPS()


# FILE CONFIG
# image_dilate int
# image_threshold int
# image_kernel_size int


class Frame:
    __slots__ = "pos", "array"

    def __init__(self, pos, array):
        self.pos = pos
        self.array = array


class RawFrame:
    __slots__ = "nmarkers", "mpoints"

    def __init__(self, n, points):
        self.nmarkers = n
        self.mpoints = points


class MarkersFinder:

    def __init__(self, config):
        self.config = config
        self.dilate = config.getint("image", "dilate")
        self.threshold = config.getint("image", "threshold")
        self.kernel_size = config.getint("image", "kernel_size")

    def binaryTransform(self, image):
        u"""Transforma la imagen en binaria."""
        gray = cv2.cvtColor(image, 6)
        binary = cv2.threshold(gray, self.threshold, 255., 0)[1]
        if self.dilate:
            kernel = np.ones((3, 3), np.uint8)
            binary = cv2.dilate(binary, self.kernel_size, iterations=5)
        return binary

    @staticmethod
    def contours(image):
        u"""Encuentra dentro del cuadro los contornos de los marcadores."""
        contours, __ = cv2.findContours(image, 0, 2)
        return [[], ] if contours is None else contours

    @staticmethod
    def contour_center(contour):
        u"""Devuelve el centro del contorno."""
        x, y, w, h = cv2.boundingRect(contour)
        return x + w/2, y + h/2

    def centers(self, contours):
        u"""Obtiene los centros de los contornos como un arreglo de numpy."""
        ccenters = [self.contour_center(c) for c in contours]
        arraycenters = np.array(ccenters, dtype=np.int16)[::-1]
        return len(ccenters), arraycenters.ravel()

    def findMarkers(self, frame):
        u"""Devuelve el número de marcadores encontrados y sus centros."""
        contours = self.contours(self.binaryTransform(frame.frame))
        return self.centers(contours)


# schema_markers_num
# schema_regions_num

class FrameDrawings:

    def __init__(self, config):
        self.markers_num = config.getint("schema", "markers_num")
        self.regions_num = config.getint("schema", "regions_num")

    def reshape(array, kind):
        u"""Modifica la forma del arreglo. Las opciones son marcadores o regiones"""
        shape = {
            "markers": (self.markers_num, 2),
            "regions": (self.regions_num, 2, 2)
        }
        return np.reshape(array, shape[kind])

    def getColors(self, num_of_markers, sameforall=True):
        u"""."""
        if sameforall:
            return np.repeat((0, 0, 255), num_of_markers)
        else:
            colors = np.zeros((num_of_markers, 3))
            variation = np.linspace(0, 255, num_of_markers)
            colors[:, 1] = variation
            colors[:, 2] = variation[::-1]
            return colors

    def drawMarkers(self, image, markers, colors):
        u"""Dibuja los marcadores en la imagen."""
        for m, c in zip(self.reshape(markers, "markers"), colors):
            cv2.drawMarker(image, tuple(m), 10, c, 1, 30)

    def drawRegions(self, image, regions, condition):
        u"""Dibuja las regiones de agrupamiento en la imagen."""
        color = (
            (0, 0, 255),  # rojo para condición 0
            (0, 255, 0)  # verde para condición 1
        )
        for (p0, p1), c in zip(self.reshape(regions, "regions"), condition):
            cv2.rectangle(image, tuple(p0), tuple(p1), color[c], 3)

    def drawNumIndicator(self, image, num_of_markers):
        u"""Dibuja el indicador de marcadores encontrados."""
        backward = {
            "color": (0, 0, 0),
            "center": (100, 100),
            "radius": 50
        }
        facetext = {
            "org": (80, 115),
            "fontFace": 0,
            "fontScale": 2,
            "color": (255, 255, 255)
        }
        cv2.circle(image, **backward)
        cv2.putText(image, str(num_of_markers), **facetext)


class Player(VideoReader):

    def __init__(self, config):
        super().__init__(config)
        self.drawings = FrameDrawings(config)

    def play(self, source, kind="raw", duration="raw", **kwargs):
        u"""Generador de cuadros de video para la reproducción en GUI.

        arguments:
        =========
            source: ruta del archivo de video.
            kind: tipo de reproducción de video [raw, walk, cycle].
            duration: la duración en cuadros de video.
            kwargs: diccionario que contiene órdenes de dibujo.
                 - rawframe: objeto para dibujar cuadros sin información
                   específica.
                 - walk: objeto con información de caminata.
                 - cycle: objeto con información de ciclo.
        """
        self.open(source)

        drawing_kind = {
        "raw": self.rawFrame,
        "walk": self.walkFrame,
        "cycle": self.cycleFrame
        }

        draw = drawing_kind[options["kind"]]

        duration_option = {
            "raw": (0, self.reader.numframes),
            "walk": (kwargs["walk"].startframe, kwargs["walk"].stopframe),
            "cycle": (kwargs["cycle"].startframe, kwargs["cycle"].stopframe),
        }

        start, stop = duration_option[duration]
        self.posframe = start

        for __ in range(stop - start):
            __, pos, frame = self.read()
            draw(frame, pos, **kwargs)
            yield frame

    def rawFrame(self, frame, pos, **kwargs):
        u"""Dibuja los marcadores sin identificar."""
        rawframe = kwargs["rawframe"]
        self.drawings.drawNumIndicator(frame, rawframe.nmarkers)
        colors = self.drawings.getColors(rawframe.nmarkers)
        self.drawings.drawMarkers(frame, rawframe.mpoints, colors)

    def walkFrame(self, frame, pos, **kwargs):
        u"""Dibuja los marcadores identificados por región."""
        walk = kwargs["walk"]
        colors = self.drawings.getColors(walk.nmarkers, False)
        self.drawings.drawMarkers(frame, walk.mpoints[pos])
        self.drawings.drawRegions(frame, walk.rpoints[pos], walk.condition[pos])

    def cycleFrame(self, frame, pos, **kwargs):
        u"""Dibuja los marcadores dentro del ciclo."""
        return NotImplemented


# explorer_empty_frame_limit
class Explorer(VideoReader):

    def __init__(self, config, container=[]):
        super().__init__(config)
        self.finder = MarkersFinder(config)
        self.container = container

        # FLAGS
        self.walking = False
        self.zero_flag = 0
        self.current_walk = None
        self.limit_zero_flag = config.getint("explorer", "empty_frame_limit")
        self.expected_markers_count = config.getint("schema", "markers_num")

    def read(self):  # se sobreescribe el método original.
        u"""Lectura de cuadro de video."""
        ret, array = self.capture.read()
        pos = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
        return ret, pos, Frame(pos, array)

    def initializingWalkingState(self):
        u"""Inicializa una caminata."""
        self.current_walk = Walk(self.config)
        self.container.append(self.current_walk)
        self.walking = True

    def finishingWalkingState(self):
        u"""Finaliza la caminata activa."""
        self.current_walk.stop()
        self.current_walk = None
        self.walking = False

    def checkingStopWalking(self, num_of_markers):
        u"""Establece la condición de detener la caminata a verdadero."""
        if num_of_markers == 0:
            self.zero_flag += 1
        else:
            self.zero_flag = 0

        if self.zero_flag > self.limit_zero_flag:
            return True
        else:
            return False

    def findWalks(self, source,):
        u"""Realiza la búsqueda de caminatas dentro del video."""
        self.open(source)

        while True:
            ret, pos, frame = self.read()
            if not ret:
                break

            # getting markers data.
            markers_num, markers_points = self.finder.findMarkers(frame)
            frame_is_fullschema = (markers_num == self.expected_markers_count)
            walking_data = (pos, frame_is_fullschema, markers_points)

            # exploring walking state.
            if not self.walking and frame_is_fullschema:
                self.initializingWalkingState()
                # adding first walking_data
                self.current_walk.insert(*walking_data)

            else:
                # adding regular walking data
                self.current_walk.insert(*walking_data)

                # check for stop signal.
                stop_walking = self.checkingStopWalking(markers_num)
                if stop_walking:
                    self.finishingWalkingState()
