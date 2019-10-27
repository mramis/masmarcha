#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2019  Mariano Ramis

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


import time
import queue
import threading

from kivy.clock import Clock
from kivy.core.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.graphics.texture import Texture

from core.video import VideoReader, VideoDrawings, VideoWriter
from core.threads import Consumer


class Frame(GridLayout):

    def show(self, image):
        u"""Presenta la imagen de video en el display."""
        self.ids.display.texture = self.image_to_texture(image)

    def image_to_texture(self, image):
        u"""Imagen(numpy.array) a textura."""
        height, width = image.shape[:2]
        texture = Texture.create(size=(width, height), colorfmt="bgr")
        texture.blit_buffer(
            image.tostring(), colorfmt='bgr', bufferfmt='ubyte')
        return texture

    def default_texture(self, wich="default"):
        u"""Textura de imagen-logo de masmarcha reproductor."""
        return Image(self.default_image).texture

    def writing_texture(self):
        u"""Textura de escritura del reproductor."""
        return Image(self.writing_image).texture

    def set_default_screen(self):
        u"""Muestra la imagen-logo de masmarcha en pantalla."""
        self.ids.display.texture = self.default_texture()

    def set_writing_screen(self):
        u"""Muestra la imagen de "grabación en proceso" en pantalla."""
        self.ids.display.texture = self.writing_texture()

    def stop_showing(self):
        u"""Detiene la reproducción de imágenes en pantalla."""
        self.set_default_screen()


class VideoImagePlayer(Consumer):

    def __init__(self, frame, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = None
        self.image = None
        self.frame = frame

    def update(self, dt):
        if self.image is not None:
            self.frame.show(self.image)

    # NOTE: sobreescribiendo Base
    def setup(self):
        dt = self.config.getfloat("video", "delay")
        self.task = Clock.schedule_interval(self.update, dt)

    # NOTE: sobreescribiendo Base
    def consume(self, image):
        self.image = image

    # NOTE: sobreescribiendo Base
    def after_run(self):
        Clock.unschedule(self.task)
        time.sleep(0.1)
        self.frame.stop_showing()


class VideoUtil(GridLayout):
    state = None
    stop_flag = None

    @property
    def frame(self):
        return self.ids.frame

    def play(self):
        u"""Reproduce en pantalla el archivo de video seleccionado."""
        reading_queue = queue.Queue(maxsize=1)
        drawing_queue = queue.Queue(maxsize=1)
        stop_reading_flag = threading.Event()
        stop_showing_flag = threading.Event()

        r = VideoReader(
            reading_queue, stop_reading_flag, config=self.config)

        d = VideoDrawings(
            reading_queue, stop_reading_flag,
            drawing_queue, stop_showing_flag, config=self.config)

        p = VideoImagePlayer(
            self.frame,
            drawing_queue, stop_showing_flag, config=self.config)

        r.start()
        d.start()
        p.start()

        self.state = "playing"
        self.stop_flag = stop_reading_flag

    def record(self):
        u"""Inicia la grabación de video (sin visualización)."""
        self.frame.set_writing_screen()

        reading_queue = queue.Queue(maxsize=1)
        stop_reading_flag = threading.Event()

        r = VideoReader(reading_queue, stop_reading_flag, config=self.config)
        w = VideoWriter(reading_queue, stop_reading_flag, config=self.config)

        r.start()
        w.start()

        self.state = "recording"
        self.stop_flag = stop_reading_flag

    def stop(self):
        u"""Detiene la actividad."""
        self.stop_flag.set()
        time.sleep(0.1)
        self.frame.stop_showing()
