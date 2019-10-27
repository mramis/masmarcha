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

import cv2
import numpy as np

from .walk import Walk
from .threads import Producer, Consumer
from .database import SqliterInserter


FOURCC = cv2.VideoWriter_fourcc(*"XVID")


class VideoReader(Producer):
    capture = None
    is_opened = False

    def __del__(self):
        super().__del__()
        if self.is_opened:
            self.capture.release()

    @property
    def posframe(self):
        u"""Devuelve la posición del cuadro a leer."""
        if self.is_opened:
            return int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))

    @posframe.setter
    def setPosFrame(self, position):
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
        """Lectura de un cuadro de video de la captura inicializada por open.
        """
        return (time.time_ns(), *self.capture.read())

    def findSource(self):
        u"""Inicia la captura en un hilo separado."""
        try:  # dispositivo (int)
            source = self.config.getint("current", "source")
        except ValueError:  # archivo de video (string)
            source = self.config.get("current", "source")
        return source

    # NOTE: Sobreescribiendo
    def setup(self):
        """Inicializa el objeto de captura cuando se llama a Producer.start
        """
        self.open(self.findSource())

    # NOTE: Sobreescribiendo
    def produce(self):
        timestamp, retrieve, frame = self.read()
        if not retrieve:
            self.resource_avaible = False
            return False
        self.resource = (timestamp, frame)
        return True


class FrameCounter:
    u"""Esta clase esta hecha para contar los frames por segundos en la
        escritura de video."""

    def __init__(self):
        self.start_time = 0
        self.final_time = 1
        self.count = 0

    def __call__(self):
        self.count += 1

    def start(self):
        u"""Inicia el contador de tiempo."""
        self.start_time = time.time()

    def stop(self):
        u"""Finaliza el contador de tiempo."""
        self.final_time = time.time()


class VideoWriter(Consumer):
    count = FrameCounter()
    is_opened = False

    def open(self):
        u"""Inicializa el objeto que escribe en disco."""
        w = self.config.getint("frame", "width")
        h = self.config.getint("frame", "height")
        filename = os.path.join(
            self.config.get("paths", "video"),
            self.config.get("video", "filename")
        )
        self.writer = cv2.VideoWriter(filename, FOURCC, 120, (w, h))
        self.is_opened = True
        self.count.start()

    def write(self, frame):
        u"""Escribe el cuadro de video."""
        self.writer.write(frame)
        self.count()

    def sqliteInsert(self):
        u"""Almacena en la base de datos información de la captura."""
        values = (
            time.strftime("%d%m%y%H%M%S"),
            self.config.get("video", "filename"),
            time.strftime("%d/%m/%y"),
            self.count.count,
            self.count.final_time - self.count.start_time,
        )
        SqliterInserter(self.config).insertVideo(values)

    # NOTE: Sobreescribiendo Base
    def setup(self):
        """Inicializa el objeto de captura cuando se llama a Consumer.start
        """
        self.open()

    # NOTE: Sobreescribiendo Base
    def consume(self, value):
        __, frame = value
        self.write(frame)

    # NOTE: Sobreescribiendo Base
    def after_run(self):
        self.count.stop()
        self.sqliteInsert()
        self.writer.release()


class MarkersFinder:

    def __init__(self, config):
        self.config = config

    def __call__(self, frame):
        return self.find(frame)

    def find(self, frame):
        u"""Devuelve el número de marcadores encontrados y sus centros."""
        dilate = self.config.getboolean("image", "dilate")
        btfunc = {True: self.dilatedBinaryTransform,
                  False: self.binaryTransform}
        contours = self.contours(btfunc[dilate](frame))
        return self.centers(contours)

    def binaryTransform(self, image):
        u"""Transforma la imagen en binaria."""
        gray = cv2.cvtColor(image, 6)
        thres = self.config.getint("image", "threshold")
        binary = cv2.threshold(gray, thres, 255, 0)[1]
        return binary

    def dilatedBinaryTransform(self, image):
        u"""Toma la imagen binaria y la dilata según indicaciones del usuario.
        """
        niterations = self.config.getint("image", "dilate_iterations")
        kernel_size = self.config.getint("image", "dilate_kernel_size")
        kernel = np.ones((kernel_size,  kernel_size), np.uint8)
        binary = cv2.dilate(self.binaryTransform(image),
                            kernel, iterations=niterations)
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
        u"""Devuelve los centros de los contornos como un arreglo de numpy."""
        ccenters = [self.contour_center(c) for c in contours]
        arraycenters = np.array(ccenters, dtype=np.int16)[::-1]
        return len(ccenters), arraycenters.ravel()


class Color:

    def redColor(self, num):
        return ((0, 0, 255) for __ in range(num))


class VideoDrawings(Consumer):

    def __init__(self, cqueue, cevent, pqueue, pevent, config):
        super().__init__(cqueue, cevent, config=config)
        self.become_intermediary(pqueue, pevent, name="Drawings")
        self.markers_num = config.getint("schema", "markers_num")
        self.regions_num = config.getint("schema", "regions_num")

        self.kind = self.config.get("current", "draw_kind")

    # NOTE: se sobreescribe el método del thread.
    def consume(self, value):
        __, frame = value
        self.draw(frame)
        return cv2.flip(frame, 0)

    def draw(self, image):
        draw = {"raw": self.rawDrawing}
        draw[self.kind](image)

    def reshape(self, kind, array, num):
        u"""Modifica la forma del arreglo según sea marcadores o regiones."""
        shape = {"markers": (num, 2), "regions": (num, 2, 2)}
        return np.reshape(array, shape[kind])

    def rawDrawing(self, image):
        u"""Se dibujan los marcadores encontrados en el cuadro de video."""
        color = Color()
        num, markers = MarkersFinder(self.config)(image)
        self.drawMarkers(image, markers, num, color.redColor(num))

    def drawMarkers(self, image, markers_array, markers_num, colors):
        u"""Dibuja los marcadores en la imagen."""
        markers = self.reshape("markers", markers_array, markers_num)
        for marker, color in zip(markers, colors):
            cv2.circle(image, tuple(marker), 10, color, -1)

#    def drawRegions(self, image, regions, condition):
#        u"""Dibuja las regiones de agrupamiento en la imagen."""
#        color = (
#            (0, 0, 255),  # rojo para condición 0
#            (0, 255, 0)  # verde para condición 1
#        )
#        for (p0, p1), c in zip(self.reshape(regions, "regions"), condition):
#            cv2.rectangle(image, tuple(p0), tuple(p1), color[c], 3)


class WalkFinder(Consumer):

    def __init__(self, config, buffer, walks_container=[]):
        self.buffer = buffer
        self.container = walks_container

        # FLAGS
        self.walking = False
        self.zero_flag = 0
        self.current_walk = None
        self.limit_zero_flag = config.getint("explorer", "empty_frame_limit")
        self.expected_markers_count = config.getint("schema", "markers_num")

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

    def shouldStopWalking(self, num_of_markers):
        u"""Establece la condición de detener la caminata a verdadero."""
        self.checkStopFlag(num_of_markers)
        if self.zero_flag > self.limit_zero_flag:
            return True
        else:
            return False

    def checkStopFlag(self, num_of_markers):
        u"""Regula el valor de la señal de detener la caminata."""
        if num_of_markers == 0:
            self.zero_flag += 1
        else:
            self.zero_flag = 0

    def findWalks(self):
        u"""Realiza la búsqueda de caminatas dentro del video."""
        finder = MarkersFinder(self.config)

        while not self.stopper.is_set():
            pos, frame = self.buffer.get()
            # getting markers data.
            num, markers = finder(frame)
            fullschema = (num == self.expected_markers_count)
            walking_data = (pos, fullschema, markers)

            # exploring walking state.
            if not self.walking and fullschema:
                self.initializingWalkingState()
                # adding first walking_data
                self.current_walk.insert(*walking_data)

            elif self.walking:
                # adding regular walking data
                self.current_walk.insert(*walking_data)

                # check for stop signal.
                stop_walking = self.shouldStopWalking(num)

                if stop_walking:
                    self.finishingWalkingState()
