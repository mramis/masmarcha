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
    x, Y, w, h = cv2.boundingRect(contour)
    return np.array(((x, x+w), (Y, Y+h))).mean(axis=1, dtype=np.int)


def roi_dsg(array, width=1.35):
    u"""Segmentación por defecto de las regiones de interés.

    :param array: arreglo con los centros de los marcadores.
    :type array: np.ndarray
    """
    top = array.min(axis=0)[-1]
    bottom = array.max(axis=0)[-1]
    distance = (bottom - top) / 6.0
    regions = []
    for i in 1, 3, 6:
        middle = (top + distance*i)
        regions.append((middle - distance*width, middle + distance*width))
    return regions


def partitions(array, regions_of_insterest):
    t, k, a = regions_of_insterest
    Y = array[:, 1] if array.any() else ()
    trunk = np.logical_and(Y > t[0], Y < t[1])
    knee = np.logical_and(Y > k[0], Y < k[1])
    ankle = np.logical_and(Y > a[0], Y < a[1])
    partitions = {
        'trunk': array[trunk],
        'knee': array[knee],
        'ankle': array[ankle]
    }
    return partitions


def set_spatial_references(markers):
    u"""Establece los parametros espaciales de referencia.

    Roi
    Unidad de espacio.
    """
    return roi_dsg(markers)


def get_markers_center(frame, umbral=240., apply_gaussian_filter=False):
    u"""."""
    gray = cv2.cvtColor(frame, 6)
    if apply_gaussian_filter:
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
    __, binary = cv2.threshold(gray, umbral, 255., 0)
    __, contours, __ = cv2.findContours(binary, 0, 2)
    markers = np.array(map(center_of_square, contours))
    return len(markers), markers


video_path = '/home/mariano/Descargas/VID_20170720_132629833.mp4'
video_obj = cv2.VideoCapture(video_path)

ret, frame = video_obj.read()
spatial_settings_OK = False
while ret:
    n_markers, markers = get_markers_center(frame, apply_gaussian_filter=1)
    if n_markers == 7:  # Que es el número de marcadores que esperamos ver en
        # este momento del desarrollo...
        roi = set_spatial_references(markers)
        spatial_settings_OK = True
    if spatial_settings_OK:
        segments = partitions(markers, roi)
        T = segments['ankle']
        for n, center in enumerate(T):
            cv2.circle(frame, (center[0], center[1]), 7, (0, 0, 255), -1)
            # cv2.putText(
            #     frame,
            #     str(n),
            #     (center[0], center[1]),
            #     cv2.FONT_HERSHEY_SIMPLEX,
            #     1,
            #     (255, 0, 0)
            # )

    cv2.imshow(
        'frame',
        cv2.resize(frame, None, fx=.4, fy=.4, interpolation=cv2.INTER_LINEAR)
    )
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    ret, frame = video_obj.read()
    sleep(.1)

video_obj.release()
cv2.destroyAllWindows()
