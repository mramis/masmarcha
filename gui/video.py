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

from kivy.uix.gridlayout import GridLayout

from gui.frame import Frame
from core.video import VideoReader, VideoWriter


class VideoUtil(GridLayout):
    buffer = queue.Queue(maxsize=1)
    stopper = threading.Event()
    activity = "playing"

    def clear_buffer(self):
        u"""Limpia el buffer de video."""
        while not self.buffer.empty():
            self.buffer.get()

    def play(self):
        u"""Muestra el archivo de video seleccionado."""
        self.state = "playing"
        self.stopper.clear()
        self.ids.frame.play_video(self.buffer)
        VideoReader(self.buffer, self.stopper, self.config).start()

    def stop(self):
        u"""Detiene la actividad."""
        which_stop = {
        "playing": self.ids.frame.stop_playing,
        "recording": self.ids.frame.stop_recording
        }
        self.stopper.set()
        self.clear_buffer()
        which_stop[self.activity]()

    def record(self):
        u"""Inicia la grabación de video (sin visualización)."""
        self.state = "recording"
        self.stopper.clear()
        self.ids.frame.record_video()
        reader = VideoReader(self.buffer, self.stopper, self.config).start()
        writer = VideoWriter(self.buffer, self.stopper, self.config).start()
