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

import os
import sys
from json import load

from configparser import ConfigParser
from io import StringIO

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, 'src')

import video

string_config = """
[paths]
schema = /home/mariano/masmarcha/schema7.json
cameracalib = /home/mariano/masmarcha/cameracalib
currentcamera = /home/mariano/masmarcha/calibration/MOTOG3-Mariano.npz

[video]
thresh = 250.0
dilate = False
"""

config = ConfigParser()
config.read_file(StringIO(string_config))

schema = load(open(config.get('paths', 'schema')))


def test_video():
    path = '/home/mariano/masmarcha/capturas/belenhidalgo.mp4'
    # Se crea el objeto
    v = video.Video(path, config)
    # Se le da posición al cuadro para que haya marcadores en escena.
    v.vid.set(video.cv2.CAP_PROP_POS_FRAMES, 100)
    # se hace una lectura del cuadro.
    frame1 = v.read_frame()
    assert(v.posframe == 0)
    assert(isinstance(v.read_frame(), np.ndarray))
    # se setean los atributos de la camara calibrada.
    assert(v.calibration is False)
    v.load_calibration_params()
    assert(v.calibration is True)
    # se posiciona 100 nuevamentes.
    v.vid.set(video.cv2.CAP_PROP_POS_FRAMES, 100)
    frame2 = v.read_frame()
    equals = frame1.flatten() == frame2.flatten()
    assert(any(equals))
    assert(not all(equals))
    # Exploración del video.
    v.explore()

def test_frame():
    pass


def test_walk():
    pass

# def test_interpolate():
#     # Las regiones son arreglos de dos vectores en el plano que apuntan a las
#     # esquinas de un rectángulo, en el que se encuentran los marcadores.
#     v11 = np.array(((1, 1), (3, 3)))
#     v21 = v11.copy()
#     v21[:, 1] += 3
#     v31 = v21.copy()
#     v31[:, 1] += 3
#
#     R1 = np.array((v11, v21, v31))
#     R2 = R1 + np.array((3, 0))
#
#     # Esta es la respuesta a la interpolacion con un punto intermedio.
#     vr = np.array((((2.5, 1), (4.5, 3)),
#     ((2.5, 4), (4.5, 6)),
#     ((2.5, 7), (4.5, 9)))).flatten()
#
#     R = video.interpolate_lost_regions(
#     (np.array((0, *R1.flatten())),
#     np.array((2, *R2.flatten()))),
#     schema)
#
#     assert(all(R[0, 1:] == vr))
#
#     # plt.plot(*v11.T, 'b-')
#     # plt.plot(*v21.T, 'r-')
#     # plt.plot(*v31.T, 'g-')
#
#     # v12, v22, v32 = R2
#     # plt.plot(*v12.T, 'b-')
#     # plt.plot(*v22.T, 'r-')
#     # plt.plot(*v32.T, 'g-')
#
#     # v1, v2, v3 = R[0, 1:].reshape(3, 2, 2)
#     # plt.plot(*v1.T, 'b--')
#     # plt.plot(*v2.T, 'r--')
#     # plt.plot(*v3.T, 'g--')
#
#     # plt.savefig('test/interpolate')


# def test_calibrate():
#     path = '/home/mariano/masmarcha/capturas/damero.mp4'
#     video.calibrate_camera(path, os.path.join('./test','MOTOG3'), (8, 4), 10,
#                            config)


# def test_distance():
#     u"""."""
#     path = "/home/mariano/masmarcha/capturas/calb-dist-tomi.mp4"
#     assert(isinstance(video.get_distance_scale(path, 0.3), float))


# def test_contours():
#     path = "/home/mariano/masmarcha/capturas/calb-dist-tomi.mp4"
#     with video.open_video(path) as vid:
#         __, frame = vid.read()
#         contours = video.find_contours(frame, dilate=True)
#         center =  video.contour_center(contours[0])
#         array_of_centers = video.contour_centers_array(contours)


# def test_getfps():
#     path = "/home/mariano/masmarcha/capturas/calb-dist-tomi.mp4"
#     assert(isinstance(video.get_fps(path), float))


# def test_openvideo():
#     path = "/home/mariano/masmarcha/capturas/calb-dist-tomi.mp4"
#     with video.open_video(path) as vid:
#         assert(isinstance(vid, video.cv2.VideoCapture))
