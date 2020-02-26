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


import cv2
import numpy as np


class MarkersFinder:

    def __init__(self, config):
        self.config = config

    def __call__(self, frame):
        return self.find(frame)

    def find(self, frame):
        u"""Devuelve el número de marcadores encontrados y sus centros."""
        dilate = self.config.getboolean("image", "dilate")
        btfunc = {True: self.dilatedBinaryTransform,
                  False: self.binaryTransform}
        contours = self.contours(btfunc[dilate](frame))
        return self.centers(contours)

    def binaryTransform(self, image):
        u"""Transforma la imagen en binaria."""
        gray = cv2.cvtColor(image, 6)
        thres = self.config.getint("image", "threshold")
        binary = cv2.threshold(gray, thres, 255, 0)[1]
        return binary

    def dilatedBinaryTransform(self, image):
        u"""Toma la imagen binaria y la dilata según indicaciones del usuario.
        """
        niterations = self.config.getint("image", "dilate_iterations")
        kernel_size = self.config.getint("image", "dilate_kernel_size")
        kernel = np.ones((kernel_size,  kernel_size), np.uint8)
        binary = cv2.dilate(self.binaryTransform(image),
                            kernel, iterations=niterations)
        return binary

    @staticmethod
    def contours(image):
        u"""Encuentra dentro del cuadro los contornos de los marcadores."""
        contours, __ = cv2.findContours(image, 0, 2)
        return [[], ] if contours is None else contours

    @staticmethod
    def contour_center(contour):
        u"""Devuelve el centro del contorno."""
        x, y, w, h = cv2.boundingRect(contour)
        return x + w/2, y + h/2

    def centers(self, contours):
        u"""Devuelve los centros de los contornos como un arreglo de numpy."""
        ccenters = [self.contour_center(c) for c in contours]
        arraycenters = np.array(ccenters, dtype=np.int16)[::-1]
        return len(ccenters), arraycenters.ravel()


class Color:

    def redColor(self, num):
        return ((0, 0, 255) for __ in range(num))


class Drawings:

    def __init__(self, config):
        self.config = config
        self.kind = self.config.get("current", "draw_kind")
        self.markers_num = config.getint("schema", "markers_num")
        self.regions_num = config.getint("schema", "regions_num")

    def draw(self, image):
        draw = {"raw": self.rawDrawing}
        draw[self.kind](image)
        return cv2.flip(image, 0)

    def reshape(self, kind, array, num):
        u"""Modifica la forma del arreglo según sea marcadores o regiones."""
        shape = {"markers": (num, 2), "regions": (num, 2, 2)}
        return np.reshape(array, shape[kind])

    def rawDrawing(self, image):
        u"""Dibuja los contornos encontrados en el cuadro."""
        color = Color()
        num, markers = MarkersFinder(self.config)(image)
        self.drawMarkers(image, markers, num, color.redColor(num))

    def drawMarkers(self, image, markers_array, markers_num, colors):
        u"""Dibuja los marcadores en la imagen."""
        markers = self.reshape("markers", markers_array, markers_num)
        for marker, color in zip(markers, colors):
            cv2.circle(image, tuple(marker), 10, color, 2)


#    def drawRegions(self, image, regions, condition):
#        u"""Dibuja las regiones de agrupamiento en la imagen."""
#        color = (
#            (0, 0, 255),  # rojo para condición 0
#            (0, 255, 0)  # verde para condición 1
#        )
#        for (p0, p1), c in zip(self.reshape(regions, "regions"), condition):
#            cv2.rectangle(image, tuple(p0), tuple(p1), color[c], 3)
