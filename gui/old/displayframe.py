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


class DisplayFrame(GridLayout):
    play = BooleanProperty(None)
    buffer = None
    schedule = None

    @property
    def default_texture(self):
        u"""Muestra la imagen por defecto del reproductor."""
        return Image(self.default_image).texture

    def frame_texture(self):
        u"""Devuelve el cuadro de video como una textura."""
        buf = next(self.buffer)
        text = Texture.create(size=(buf.width, buf.height), colorfmt="bgr")
        text.blit_buffer(buf.frame.tostring(), colorfmt='bgr', bufferfmt='ubyte')
        return text

    def player_video(self):
        u"""Reproduce el video."""
        delay = self.core.config.getfloat("video", "delay")
        self.buffer = self.core.videoPlayer()
        self.schedule = Clock.schedule_interval(self.update, delay)

    def on_play(self, instance, value):
        u"""Determina la acción del widget: Reproducir o detenerse."""
        if value is True:
            self.player_video()
        else:
            self.stop_playing()

    def stop_playing(self):
        u"""Detiene la reproducción del video."""
        if self.schedule is None:
            return
        Clock.unschedule(self.schedule)
        self.schedule = None
        self.ids.display.texture = self.default_texture

    def update(self, dt):
        u"""Presenta la imagen de video en el display."""
        try:
            self.ids.display.texture = self.frame_texture()
        except StopIteration:
            self.play = False
