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

from .threads import Producer, Consumer
from .database import SqliterInserter


FOURCC = cv2.VideoWriter_fourcc(*"XVID")


class VideoReader(Producer):

    def __init__(self, config, **kwargs):
        super().__init__(name="VideoReader")
        self.config = config
        self.capture = None
        self.is_opened = False

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
    def posframe(self, position):
        u"""Establece la pocisión inicial (cuadro) de lectura de video."""
        if self.is_opened:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, position)

    @property
    def numframes(self):
        """Devuelve la cantidad de cuadros del video."""
        if self.is_opened:
            return int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def find_source(self):
        u"""Devuelve la fuente que se utilizará para la captura de video."""
        # El usuario decide fuente de la captura.
        try:  # dispositivo (int)
            source = self.config.getint("current", "source")
        except ValueError:  # archivo de video (string)
            source = self.config.get("current", "source")
        return source

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

    # NOTE: Sobreescribiendo Base
    def setup_thread(self):
        """Establece los parametros de la captura de video."""
        self.name = "VideoReader"
        self.open(self.find_source())
        # el usuario puede o no agregar demora en la produción de cuadros.
        self.production_delay = self.config.getfloat("video", "delay")

    # NOTE: Sobreescribiendo Base
    def produce_in_thread(self):
        u"""Produce los cuadros de video para agregarlos a la cola de
        lectura."""
        __, retrieve, frame = self.read()
        return retrieve, frame


class VideoFramesCounter:
    u"""Esta clase esta hecha para contar los frames por segundos en la
        escritura de video."""

    def __init__(self):
        self.t0 = 0
        self.t1 = 0
        self.counter = 0

    def __call__(self):
        self.counter += 1

    def start(self):
        u"""Inicia el contador de tiempo."""
        self.t0 = time.time()

    def stop(self):
        u"""Finaliza el contador de tiempo."""
        self.t1 = time.time()

    def summary(self):
        u"""."""
        return (self.counter, self.t1 - self.t0)


class VideoWriter(Consumer):

    def __init__(self, config, **kwargs):
        super().__init__(name="VideoWriter")
        self.config = config
        self.capture = None
        self.counter = VideoFramesCounter()
        self.is_opened = False

    def __del__(self):
        super().__del__()
        if self.is_opened:
            self.capture.release()

    def open(self):
        u"""Inicializa el objeto que escribe en disco."""
        w = self.config.getint("frame", "width")
        h = self.config.getint("frame", "height")
        filename = os.path.join(
            self.config.get("paths", "video"),
            self.config.get("video", "filename")
        )
        self.capture = cv2.VideoWriter(filename, FOURCC, 120, (w, h))
        self.is_opened = True

    def write(self, frame):
        u"""Escribe el cuadro de video."""
        self.capture.write(frame)
        self.counter()

    def sqlite_insert_video(self):
        u"""Almacena en la base de datos información de la captura."""
        values = (
            time.time(),
            self.config.get("video", "filename"),
            *self.counter.summary())
        SqliterInserter(self.config).insertVideo(values)

    # NOTE: Sobreescribiendo Base
    def setup_thread(self):
        """Establece los parametros de la captura de video."""
        self.name = "VideoWriter"
        self.open()
        self.counter.start()

    # NOTE: Sobreescribiendo Base
    def consume_in_thread(self, value):
        u"""Recive los cuadros de la cola de lectura los escribe en disco."""
        self.write(value)

    # NOTE: Sobreescribiendo Base
    def last_thread_execution(self):
        u"""Ingresa datos de escritura en la base sqlite."""
        self.counter.stop()
        self.sqlite_insert_video()
