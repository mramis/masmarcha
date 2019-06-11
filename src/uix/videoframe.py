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

import queue
import threading

from kivy.clock import mainthread
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty

from ..video import Video, explore_video
from ..settings import app_config
from .configwidgets import BoolOption, IntegerOption, FloatOption


class VideoFrame(GridLayout):
    u"""Frame de control de video."""
    current_video = StringProperty(None, allownone=True)

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

    def load_video(self):
        """Carga el archivo de video."""
        self.video = Video(app_config)
        self.video.open(self.current_video)
        self.ids.endframe.current_value = self.video.size
        self.ids.startframe.current_value = 0

    def on_current_video(self, instance, value):
        u"""Agrega la ruta a la lista de rutas."""
        self.ids.show_file.text = value

    def show_video(self):
        u"""Muestra el archivo de video seleccionado."""
        if self.current_video is None:
            return
        # self.load_video()
        # self.video.view("preview")
        # NOTE: Nuevo desarrollo para visualizar video dentro de la app
        self.display.capture_name = self.current_video

    def explore_video(self, container):
        u"""Realiza la exploración del video en busca de caminatas."""
        if self.current_video is None:
            return
        self.load_video()
        for walk, framepos in explore_video(self.video):
            self.upload_progress(framepos)
            container.append(walk)
        self.reset_progress()

    def run_explorer_thread(self, walksdest):
        u"""Inicia la exploración en otro hilo."""
        threading.Thread(target=self.explore_video, args=(walksdest,)).start()

    @mainthread
    def upload_progress(self, progress):
        u"""Actualiza el progreso de exploración de video."""
        value = (progress / self.video.size) * 100
        self.ids.progressbar.value = value
        self.ids.progresstext.text = "Progreso {:.2f}%".format(value)

    @mainthread
    def reset_progress(self):
        self.ids.progressbar.value = 0
        self.ids.progresstext.text = "Progreso"


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    source = StringProperty(None)
