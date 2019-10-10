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
from .database import SqliterInserter


FOURCC = cv2.VideoWriter_fourcc(*"XVID")


class VideoReader:

    def __init__(self, buffer, stopper, config):
        self.config = config
        self.buffer = buffer
        self.stopper = stopper
        self.is_opened = False

    def __del__(self):
        print(f"{self.__class__.__name__} dieying...")
        self.buffer.task_done()
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
        """Lee el cuadro actual de video para escribir en disco."""
        return (None, *self.capture.read())

    def start(self):
        u"""Inicia la captura en un hilo separado."""
        try:  # dispositivo (int)
            source = self.config.getint("current", "source")
        except ValueError:  # archivo de video (string)
            source = self.config.get("current", "source")
        self.open(source)
        threading.Thread(target=self.threadingRead, args=()).start()
        return self

    def threadingRead(self):
        u"""Lee los cuadros de video según la función que se le pase y agreaga
        el cuadro al buffer.
        """
        while not self.stopper.is_set():
            pos, ret, frame = self.read()
            if not ret:
                self.stopper.set()
                break
            self.buffer.put((pos, frame))
        self.capture.release()


class FrameCounter:
    u"""Esta clase esta hecha para contar los frames por segundos en la
        escritura de video."""

    def __init__(self):
        self.start_time = 0
        self.final_time = 1
        self.frame_counter = 0

    def __call__(self):
        self.frame_counter += 1

    def start(self):
        u"""Inicia el contador de tiempo."""
        self.start_time = time.time()
    
    def stop(self):
        u"""Finaliza el contador de tiempo."""
        self.final_time = time.time()


class VideoWriter:

    def __init__(self, buffer, stopper, config):
        self.config = config
        self.buffer = buffer
        self.stopper = stopper
        # para obtener una lectura real de fps:
        self.counter = FrameCounter()

    def __del__(self):
        print(f"{self.__class__.__name__} diying...")
        self.writer.release()

    def open(self):
        u"""Inicializa el objeto que escribe en disco."""
        w = self.config.getint("frame", "width")
        h = self.config.getint("frame", "height")
        filename = os.path.join(
            self.config.get("paths", "video"),
            self.config.get("video", "filename")
        )
        self.writer = cv2.VideoWriter(filename, FOURCC, 120, (w, h))

    def write(self, frame):
        u"""Escribe el cuadro de video."""
        self.writer.write(frame)
        self.counter()

    def writeDataBase(self):
        u"""Almacena en la base de datos información de la captura."""
        values = (
            time.strftime("%d%m%y%H%M%S"),
            self.config.get("video", "filename"),
            time.strftime("%d/%m/%y"),
            self.counter.frame_counter,
            self.counter.final_time - self.counter.start_time,
        )
        SqliterInserter(self.config).insertVideo(values)

    def start(self):
        u"""Incializa el hilo de escritura."""
        self.open()
        threading.Thread(target=self.threadingWrite, args=()).start()
        return self

    def threadingWrite(self):
        u"""Captura los cuadros del buffer y los escribe en disco."""
        self.counter.start()
        while not self.stopper.is_set():
            __, frame = self.buffer.get()
            self.write(frame)
        self.counter.stop()
        self.writeDataBase()


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


class VideoDrawings:

    def __init__(self, rbuffer, sbuffer,  stopper, config):
        self.config = config
        self.reader_buffer = rbuffer
        self.screen_buffer = sbuffer
        self.stopper = stopper

        self.markers_num = config.getint("schema", "markers_num")
        self.regions_num = config.getint("schema", "regions_num")

    def __del__(self):
        print(f"{self.__class__.__name__} dying...")

    def start(self):
        u"""."""
        kind = self.config.get("current", "screen_kind")
        threading.Thread(target=self.draw, args=(kind, )).start()

    def draw(self, kind):
        u"""Dibuja sobre el cuadro de video."""
        draw = { "raw": self.rawDrawing}
        while not self.stopper.is_set():
            # obtine el cuadro del buffer de lectura.
            __, frame = self.reader_buffer.get()
            draw[kind](frame)
            # introduce el cuadro ya dibujado en el buffer de la pantalla.
            self.screen_buffer.put(cv2.flip(frame, 0))

    def reshape(self, kind, array, num):
        u"""Modifica la forma del arreglo según sea marcadores o regiones."""
        shape = {"markers": (num, 2), "regions": (num, 2, 2)}
        return np.reshape(array, shape[kind])

    def rawDrawing(self, image):
        u"""Se dibujan los marcadores encontrados en el cuadro de video."""
        color = Color()
        num, markers =  MarkersFinder(self.config)(image)
        self.drawMarkers(image, markers, num, color.redColor(num))

    def drawMarkers(self, image, markers_array, markers_num, colors):
        u"""Dibuja los marcadores en la imagen."""
        markers = self.reshape("markers", markers_array, markers_num)
        for marker, color in zip(markers, colors):
            cv2.circle(image, tuple(marker), 10, color, -1)

    def drawRegions(self, image, regions, condition):
        u"""Dibuja las regiones de agrupamiento en la imagen."""
        color = (
            (0, 0, 255),  # rojo para condición 0
            (0, 255, 0)  # verde para condición 1
        )
        for (p0, p1), c in zip(self.reshape(regions, "regions"), condition):
            cv2.rectangle(image, tuple(p0), tuple(p1), color[c], 3)


class WalkFinder:

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
                stop_walking = self.shouldStopWalking(markers_num)

                if stop_walking:
                    self.finishingWalkingState()
