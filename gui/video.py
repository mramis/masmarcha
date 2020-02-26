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

import queue
import threading

from kivy.clock import Clock
from kivy.core.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.graphics.texture import Texture

from core.image import Drawings
from core.videoio import VideoReader, VideoWriter


class Frame(GridLayout):

    def default_texture(self):
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

    def image_to_texture(self, image):
        u"""Imagen(numpy.array) a textura."""
        height, width = image.shape[:2]
        texture = Texture.create(size=(width, height), colorfmt="bgr")
        texture.blit_buffer(
            image.tostring(), colorfmt='bgr', bufferfmt='ubyte')
        return texture

    def show(self, image):
        u"""Presenta la imagen de video en el display."""
        self.ids.display.texture = self.image_to_texture(image)


class VideoPlayer:

    def __init__(self, frame, config):
        self.task = None
        self.frame = frame
        self.config = config

        self.reader = VideoReader(config)
        self.drawing = Drawings(self.config)
        self.reader.open(self.reader.find_source())

    def stop_playing(self):
        Clock.unschedule(self.task)
        self.reader.capture.release()
        self.frame.set_default_screen()
        self.task = None

    def start_playing(self):
        dt = self.config.getfloat("video", "delay")
        self.task = Clock.schedule_interval(self.update_frame, dt)

    def update_frame(self, dt):
        __, ret, image = self.reader.read()
        if ret is False:
            self.stop_playing()
            return
        self.frame.show(self.drawing.draw(image))


class VideoUtil(GridLayout):
    state = "stopped"
    queue = None
    event = None
    player = None

    @property
    def frame(self):
        return self.ids.frame

    def play(self):
        u"""Reproduce en pantalla el archivo de video seleccionado."""
        if self.state == "recording":
            return
        self.player = VideoPlayer(self.frame, self.config)
        self.player.start_playing()
        self.state = "playing"

    def record(self):
        u"""Inicia la grabación de video (sin visualización)."""
        if self.state == "playing":
            return

        self.queue = queue.Queue(maxsize=1)
        self.event = threading.Event()

        r = VideoReader(self.config)
        w = VideoWriter(self.config)

        r.start_thread(self.queue, self.event)
        w.start_thread(self.queue, self.event)

        self.frame.set_writing_screen()
        self.state = "recording"

    def stop(self):
        u"""Detiene la actividad."""
        if self.state == "playing":
            self.player.stop_playing()

        elif self.state == "recording":
            self.event.set()
            self.queue.join()
            self.frame.set_default_screen()

        self.state = "stopped"
