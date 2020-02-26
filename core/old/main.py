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

import logging

from .video import Video, View


class Core(object):
    u"""Clase principal que maneja la lógica de la aplicación."""
    __data_container = {"walks": [], "cycles": [], "parameters": []}
    __current = {"video": None, "walk": None, "cycle": None}

    def __init__(self, config, schema):
        self.view = View(config, schema)
        self.video = Video(config, schema)
        self.schema = schema
        self.config = config

    @property
    def walks(self):
        return self.__data_container["walks"]

    @property
    def cycles(self):
        return self.__data_container["cycles"]

    @property
    def parameters(self):
        return self.__data_container["parameters"]

    @property
    def walk(self):
        return self.__current["walk"]

    @walk.setter
    def walk(self, walk):
        self.__current["walk"] = walk

    def reset(self):
        u"""Se reinicia la clase."""
        self = Core()

    def loadVideo(self, filepath):
        u"""Carga el video."""
        try:
            self.video.open(filepath)
            self.__current["video"] = self.video
        except Exception as error:
            logging.error(error)
            raise Exception(error)

    def exploreVideo(self, fupdate=None):
        u"""Lanza la exploración del video."""
        if self.config.getboolean("explorer", "clearwalks"):
            self.__data_container["walks"].clear()
        for pos, walk in self.video.searchForWalks():
            self.__data_container["walks"].append(walk)
            if fupdate is not None:
                fupdate(pos)
        if fupdate is not None:
            fupdate(-1)

    def videoPlayer(self):
        u"""Devuelve el generador de cuadros de video."""
        return self.view.player(self.video, walk=self.walk)
