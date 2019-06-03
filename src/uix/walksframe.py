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

from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty

from .settings import app_config

from .video import Video, Pics


class VideoFrame(GridLayout):
    u"""Frame de control de video."""
    current_video = StringProperty(None, allownone=True)
    paths = []

    def show_load(self):
        u"""Popup para buscar la ruta del video."""
        sourcedir = app_config.get("paths", "sourcedir")
        self._content = LoadDialog(load=self.load, source=sourcedir)
        self._popup = Popup(title='Seleccionar Video', content=self._content)
        self._popup.open()

    def dismiss_popup(self):
        u"""Destruye el popup de archivos."""
        self._popup.dismiss()

    def load(self, filepath):
        u"""Establece la ruta del archivo fuente de video en el sistema."""
        value = filepath.pop(0) if filepath != [] else None
        if value is not None:
            ext = value.split('.')[-1]
            if ext in app_config.get("video", "extensions").split(','):
                self.current_video = value
                self.dismiss_popup()

    def on_current_video(self, instance, value):
        u"""Agrega la ruta a la lista de rutas."""
        self.ids.show_file.text = value
        self.paths.append(value)

    def show_video(self):
        u"""Muestra el archivo de video seleccionado."""
        video = Video(app_config)
        video.open(self.current_video)
        video.view("preview", delay=.0)
