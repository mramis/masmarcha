#!/usr/bin/env python
# coding: utf-8

"""Docstring."""

# Copyright (C) 2017  Mariano Ramis

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


import cv2
import numpy as np
from calculo.video import centroid


class Frame(object):
    u"""."""

    def __init__(self, frame, ctime):
        u"""Inicializa el Cuadro.

        :param frame: matriz de imagen de tres canales.
        :type frame: np.ndarray
        :param ctime: la posicion en el tiempo[ms] del cuadro dentro del video.
        :type ctime: float
        """
        self._frame = frame
        self.ctime = ctime

    @property
    def frame(self):
        return self._frame

    def find_markers(self, umbral=240., blur=False, blur_size=(5, 5)):
        u"""."""
        gray = cv2.cvtColor(self._frame, cv2.COLOR_BGR2GRAY)
        if blur:
            gray = cv2.GaussianBlur(gray, blur_size, 0)
        binary = cv2.threshold(gray, umbral, 255., 0)[1]
        contours = cv2.findContours(binary, 0, 2)[1]
        markers_centroid = [centroid(*cv2.boundingRect(c)) for c in contours]
        self.markers = np.array(markers_centroid)

    def partitions(self, regions_of_insterest):
        u"""Particiona el arreglo de marcadores por segmento del cuerpo.

        Este método se aplica luego de que se hayan extraido los centros de
        los marcadores. Las tres particiones que genera son: Tronco, Rodilla,
        y Tobillo. Si no se encuentra el número de marcadores que se espera por
        cada región entonces, para esa región, el valor es None.
        """
        Y = self.markers[:, 1] if self.markers.any() else ()
        regions = ('tronco', 'rodilla', 'tobillo')
        self.partitions = {}
        # Separo los marcadores por regiones.
        for roi, n, region in zip(regions_of_insterest, (2, 2, 3), regions):
            markers = self.markers[np.logical_and(Y > roi[0], Y < roi[1])]
            if markers.shape[0] != n:
                markers = None
            self.partitions[region] = markers
