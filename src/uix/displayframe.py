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
from kivy.properties import StringProperty
from kivy.core.image import Image
from kivy.clock import Clock


class DisplayFrame(GridLayout):
    capture_name = StringProperty(None)
    refresh = None

    def on_capture_name(self, instance, value):
        u"""Inicia la visualización."""
        self.video = Video(config)
        self.video.open(value)
        self.refresh = Clock.schedule_interval(
            self.update, config.getfloat("video", "delay"))

    @property
    def default_texture(self):
        return Image(self.default_image).texture

    def update(self, dt):
        ret, posframe, frame = self.video.read()
        if ret:
            # convert it to texture
            w, h, buf =  self.video.flip_and_resize(frame)
            text = Texture.create(size=(w, h), colorfmt="bgr")
            text.blit_buffer(buf.tostring(), colorfmt='bgr', bufferfmt='ubyte')
            self.ids.display.texture = text

    def stop(self):
        if self.refresh is None:
            return
        Clock.unschedule(self.refresh)
        self.video.capture.release()
        self.refresh = None
        self.ids.display.texture = self.default_texture
