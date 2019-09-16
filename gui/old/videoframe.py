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

from kivy.clock import Clock, mainthread
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty

from .configwidgets import BoolOption, IntegerOption, FloatOption


class VideoFrame(GridLayout):
    u"""Frame de control de video."""
    current_video = StringProperty(None, allownone=True)

    def show_load(self):
        u"""Popup para buscar la ruta del video."""
        sourcedir = self.core.config.get("paths", "home")
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
            if ext in self.core.config.get("video", "extensions").split('-'):
                self.current_video = value
                self.dismiss_popup()

    def on_current_video(self, instance, value):
        u"""Agrega la ruta a la lista de rutas."""
        self.ids.show_file.text = value
        self.load_video()

    def load_video(self):
        """Carga el archivo de video."""
        self.core.loadVideo(self.current_video)
        self.ids.endframe.current_value = self.core.video.duration
        self.ids.startframe.current_value = 0

    def play(self): ## Esta tiene que estar..
        u"""Muestra el archivo de video seleccionado."""
        if self.current_video is None:
            return
        self.appplayer.play = True

    def stop(self):
        u"""Detiene la reproducción."""
        self.appplayer.play = False

    def run_explorer_thread(self):
        u"""Inicia la exploración en otro hilo."""
        if self.current_video is None:
            return
        thread = threading.Thread(target=self.core.exploreVideo,
                                  args=(self.upload_progress,),
                                  daemon=True)
        thread.start()

    @mainthread
    def upload_progress(self, progress):
        u"""Actualiza el progreso de exploración de video."""
        if progress == -1:
            self.reset_progress()
            return
        value = (progress / self.core.video.duration) * 100
        self.ids.progressbar.value = value
        self.ids.progresstext.text = "Progreso {:.2f}%".format(value)

    def reset_progress(self):
        self.ids.progressbar.value = 0
        self.ids.progresstext.text = "Progreso"
        return False

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    source = StringProperty(None)
