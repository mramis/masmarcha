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
from time import sleep

# NOTE: dvp = desarrollo, no es parte del código final.


def center_of_square(contour):
    u"""Devueleve el centro de los límites (cuadrados) de un contorno."""
    x, y, w, h = cv2.boundingRect(contour)
    return np.array(((x, x+w), (y, y+h))).mean(axis=1, dtype=np.int)


def partition(array):
    u"""Genera una partición del array.

    La partición del arreglo se genera tomando en cuenta la distancia
    en las coordenadas `y`. Si los puntos están cercanos entre sí,
    entonces forman parte del mismo grupo. Esto clasifica los marcadores
    de tobillo, rodilla y cadera.
    :param array: Arreglo con los centros de los marcadores obtenidos
    de la imagen.
    :type array: np.ndarray
    """
    y_column = array[:, 1]
    safe_distance = (max(y_column) - min(y_column)) / 4  # Este número debería poder modificarse
    compare_array = np.append(y_column[1:], y_column[0])
    bool_classifier = np.abs(compare_array - y_column) < safe_distance
    indices = np.arange(y_column.size)

    group = []
    partitions = []
    for i, b in np.array((indices, bool_classifier)).transpose():
        if b is True:
            group.append(i)
        else:
            group.append(i)
            partitions.append(array[group])
            group = []
    return partitions


video_path = '/home/mariano/Descargas/VID_20170707_104121679.mp4'
video_obj = cv2.VideoCapture(video_path)

ret, frame = video_obj.read()
while ret:
    resized_frame = cv2.resize(frame, None, fx=.5, fy=.5)  # NOTE: dvp
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    # blurred = cv2.GaussianBlur(gray_frame, (3, 3), 0)  # NOTE: dvp::opcional
    __, binary = cv2.threshold(gray_frame, 240., 255., cv2.THRESH_BINARY)

    ret_imag, contours, hierarchy = cv2.findContours(
        binary.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for n, center in enumerate(map(center_of_square, contours)):
        cv2.circle(resized_frame, (center[0], center[1]), 7, (0, 0, 255), -1)
        cv2.putText(
            resized_frame,
            str(n),
            (center[0], center[1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0)
        )

    cv2.imshow('frame', resized_frame)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    ret, frame = video_obj.read()
    sleep(.3)

video_obj.release()
cv2.destroyAllWindows()
