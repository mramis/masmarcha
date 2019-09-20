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


from kivy.graphics.texture import Texture
from kivy.uix.gridlayout import GridLayout
from kivy.properties import BooleanProperty
from kivy.core.image import Image
from kivy.clock import Clock


class Frame(GridLayout):
    playing_task = None
    buffer = None

    def default_texture(self, wich="default"):
        u"""Muestra la imagen por defecto del reproductor."""
        image_dict = {
            "default": self.default_image,
            "writing": self.writing_image
        }
        return Image(image_dict[wich]).texture

    def writing_texture(self):
        u"""Muestra la imagen de escritura del reproductor."""
        return Image(self.writing_image).texture

    def buff_image_texture(self):
        u"""Devuelve el cuadro de video como una textura."""
        img = self.buffer.get()
        height, width = img.shape[:2]
        texture = Texture.create(size=(width, height), colorfmt="bgr")
        texture.blit_buffer(img.tostring(), colorfmt='bgr', bufferfmt='ubyte')
        return texture

    def play_video(self, buffer):
        u"""Reproduce el video."""
        delay = self.config.getfloat("video", "delay")
        self.buffer = buffer
        self.playing_task = Clock.schedule_interval(self.update, delay)

    def record_video(self):
        u"""Muestra en pantalla que se está grabando."""
        self.ids.display.texture = self.default_texture("writing")

    def stop_playing(self):
        u"""Detiene la reproducción del video."""
        Clock.unschedule(self.playing_task)
        self.ids.display.texture = self.default_texture()

    def stop_recording(self):
        u"""Muestra la pantalla original."""
        self.ids.display.texture = self.default_texture()

    def update(self, dt):
        u"""Presenta la imagen de video en el display."""
        self.ids.display.texture = self.buff_image_texture()
