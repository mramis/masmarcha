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
        self.capture.release()

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
        """Lee el cuadro actual de video para escribir en disco."""
        return (self.posframe, *self.capture.read())

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


class VideoWriter:

    def __init__(self, buffer, stopper, config):
        self.config = config
        self.buffer = buffer
        self.stopper = stopper
        # para obtener una lectura real de fps:
        self.final_time = 1
        self.initial_time = 0
        self.writed_frames = 0

    def __del__(self):
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
        self.writed_frames += 1

    def writeDataBase(self):
        u"""Almacena en la base de datos información de la captura."""
        values = (
            self.config.get("video", "filename"),
            time.strftime("%d/%m/%y"),
            self.writed_frames,
            self.final_time - self.initial_time,
        )
        SqliterInserter(self.config).insertVideo(values)

    def start(self):
        u"""Incializa el hilo de escritura."""
        self.open()
        threading.Thread(target=self.threadingWrite, args=()).start()
        return self

    def threadingWrite(self):
        u"""Captura los cuadros del buffer y los escribe en disco."""
        self.initial_time = time.time()
        while not self.stopper.is_set():
            __, frame = self.buffer.get()
            self.write(frame)
        self.final_time = time.time()
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


class VideoDrawings:

    def __init__(self, rbuffer, sbuffer,  stopper, config):
        self.config = config
        self.reader_buffer = rbuffer
        self.screen_buffer = sbuffer
        self.stopper = stopper

        self.markers_num = config.getint("schema", "markers_num")
        self.regions_num = config.getint("schema", "regions_num")

    def start(self):
        u"""."""
        kind = self.config.get("current", "screen_kind")
        threading.Thread(target=self.draw, args=(kind, )).start()

    def draw(self, kind):
        #NOTE: hay que seguir desde acá para los dibujos en el cuadro de video...
        self.find = MarkersFinder(self.config)
        # choose the screen kind...
        while not self.stopper.is_set():
            pos, frame = self.reader_buffer.get()
            
            num, markers = self.find(frame)
            self.drawMarkers(frame, markers, num, self.getColors(num, True))
            # Se introduce nuevamente el cuadro volteado verticalmente.
            self.screen_buffer.put(cv2.flip(frame, 0))

    def reshape(self, kind, array, num):
        u"""Modifica la forma del arreglo según sea marcadores o regiones."""
        shape = {"markers": (num, 2), "regions": (num, 2, 2)}
        return np.reshape(array, shape[kind])

    def getColors(self, num, sameforall=True):
        u"""Colores para los marcadores."""
        if sameforall:
            red_color = (0, 0, 255)
            return (red_color for __ in range(num))
        else:
            colors = ((0, 0, 255), (0, 255, 0), (255, 0, 0))
            colors = np.zeros((num, 3))
            variation = np.linspace(0, 255, num)
            colors[:, 1] = variation
            colors[:, 2] = variation[::-1]
            return colors
    
    def rawDrawing(self, image, **kwargs):


        self.drawMarkers(image,
                         kwargs['markers_array'],
                         kwargs['markers_num'],
                         kwargs['colors'])

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


# explorer_empty_frame_limit
class Explorer:

    def __init__(self, config, buffer, container=[]):
        self.buffer = buffer
        self.finder = MarkersFinder(config)
        self.container = container

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

    def findWalks(self, source,):
        u"""Realiza la búsqueda de caminatas dentro del video."""
        while not self.stopper.is_set():
            pos, frame = self.buffer.get()

            # getting markers data.
            markers_num, markers_points = self.finder.find(frame)
            frame_is_fullschema = (markers_num == self.expected_markers_count)
            walking_data = (pos, frame_is_fullschema, markers_points)

            # exploring walking state.
            if not self.walking and frame_is_fullschema:
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
