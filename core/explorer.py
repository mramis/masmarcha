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


# from .walk import Walk

import sys
import logging

import numpy as np

from core.image import MarkersFinder
from core.videoio import VideoReader

from core.arrays import VideoArray, WalkArray



class VideoExplorer:
    """Explorador de la captura de video.

    Esta clase esta diseñada para extraer los datos de los marcadores de cada
    cuadro de video y agregarlas al arreglo "General de Marcadores".
    """

    def __init__(self, config, updater=None):
        self.config = config
        self.updater = updater

    def update_progress(self):
        """Actualiza el progreso de exploración en la interfaz de usuario."""
        if self.updater is not None:
            self.updater.update()

    def explore(self):
        """Realiza la exploración del video en búsqueda marcadores.
    
        Utiliza la clase videoio.VideoReader en hilo principal (main thread).
        :return: un arreglo 2d que contiene el resultado de la exploración de
         los cuadros, con los datos de los marcadores encontrados.
        :rtype: VideoArray
        """
        video = VideoReader(self.config)
        video.open(video.find_source())

        finder = MarkersFinder(self.config)
        video_array = VideoArray(video.numframes, self.config)

        while True:
            __, ret, frame = video.read()
            if not ret:
                break
            __, markers = finder.find(frame)
            video_array.insert(markers)
            self.update_progress()

        return video_array


class VideoArrayExplorer:

    def __init__(self, config):
        self.config = config

    def __bounds(self, index):
        lim = self.config.getint("explorer", "empty_frame_limit")
        diff = np.diff(index) > lim
        # indices internos
        innerx = np.arange(index.size - 1)
        # limites derechos, limites izquierdos
        r_bounds = innerx[diff]
        l_bounds = innerx[diff] + 1
        # limites internos
        inner_bounds = np.union1d(index[r_bounds], index[l_bounds])
        # limites establecidos en la sucesión de numeros enteros con
        # una distancia de discontinuidad determinada por el usuario.
        return np.concatenate(([index[0]], inner_bounds, [index[-1]]))

    def __walks_index(self, video_array):
        nonzero_bounds = self.__bounds(video_array.nonzero())
        fullschema_bounds = self.__bounds(video_array.fullschema())

        if nonzero_bounds.size == fullschema_bounds.size:
            candidate = fullschema_bounds
        else:
            candidate = nonzero_bounds
            logging.warning(
                f"{video_array} nonzero_bounds != fullschema_bounds"
            )

        ncols = 2
        nrows = candidate.size // ncols
        return candidate.reshape(nrows, ncols)

    def get_walks(self, video_array):
        """Iterator"""
        for ix in self.__walks_index(video_array):
            a, b = ix
            walk = WalkArray(config)
            yield walk.build(video_array.view[a: b + 1])
