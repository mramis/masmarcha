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
import pickle
from configparser import ConfigParser
from io import StringIO
import logging

import numpy as np

sys.path.insert(0, 'src')

import video

string_config = """
[paths]
calibration = test/testdata
currentcamera = test/testdata/MTOG3-Mariano.npz
session = test/testdata
logging = test/testdata/masmarcha.log

[video]
thresh = 250.0
dilate = False
roiextrapixel = 35
fpscorrection = 4
framewidth = 640
frameheight = 480
calibrate = True
calibframerate = 10
chessboardwidth = 8
chessboardheight = 4
"""
path = 'test/testdata/VID_20180814_172232987.mp4'
schema = {
    "n": 7,
    "markersxroi": {0: [0, 1], 1: [2, 3], 2: [4, 5, 6]},
    "markerlabels": ["M0", "M1", "M2", "M3", "M4", "M5", "M6"],
    "segments": {"tight": ["M1", "M2"], "leg": ["M3", "M4"], "foot": ["M5", "M6"]},
    "joints": ["hip", "knee", "ankle"]}
config = ConfigParser()
config.read_file(StringIO(string_config))

<<<<<<< HEAD
schema = load(open(config.get('paths', 'schema')))
markers = dict(np.load('/home/mariano/masmarcha/session/cycle.0.walk03-Primo-Tomasmp4.npz').items())['markers']


# def test_video():
#     path = '/home/mariano/masmarcha/capturas/belenhidalgo.mp4'
#     vid = video.Video(path, config)
#
#     vid.set(video.cv2.CAP_PROP_POS_FRAMES, 100)


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


def test_distance():
    u"""."""
    path = "/home/mariano/masmarcha/capturas/"
    print()
    print(np.linalg.norm(markers[:, 3] - markers[:, 4], axis=1).mean())

    d = video.get_distance_scale(markers, 0.32)
    assert(isinstance(d, float))
    print(d)

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
=======

def test_video():
    # Creación del objeto Video
    vi = video.Video(config)
    assert(vi.vid is None)
    vi.open_video(path)
    assert(isinstance(vi.vid, video.cv2.VideoCapture))

    assert(isinstance(vi.get_fps(), float))
    ret, pos0, frame0 = vi.read_frame()
    assert(ret)
    vi.set_position(200)
    ret, pos1, frame1 = vi.read_frame()
    assert(ret)
    assert(pos0 != pos1)

    n, cmarkers = vi.find_markers(frame1)
    centers = vi.calculate_center_markers(cmarkers)

    assert(isinstance(centers, np.ndarray))
    assert(n == centers.shape[0])

    vi.cfg.set('video', 'dilate', 'True')
    n, cmarkers = vi.find_markers(frame1)

    vi.calculate_distortion_params('test/testdata/MOTOG3-DAMERO.mp4',
                                   'MTOG3-Mariano.npz')

    vi.load_distortion_params()

    vi.open_video(path)
    vi.set_position(100)
    ret, pos2, frame2 = vi.read_frame()
    assert(ret is True)

    vid = vi.vid
    del(vi)
    assert(vid.isOpened() is False)


def test_explorer():
    explorer= video.Explorer(path, schema, config)
    explorer.preview(0.0)
    explorer.find_walks()

    # se guarda una de las caminatas para el test.
    global walk
    walk = explorer.walks[0]


def test_walk():
    """Se prueba la funcionalidad de la clase walk"""
    global walk
    # Se clasifican los marcadores en esquema completo o incompleto.
    walk.classify_markers()
    # En los cuadros en los que los marcadores no presentan esquema completo
    # se calculan regiones de interés para poder encontrar los marcadores
    # faltantes y reducir la pérdidad de datos.
    walk.interp_uncompleted_regions()
    # Una ves que se identificaron los marcadores en los cuadros de esquema
    # incumpleto, se agregan al arreglo de marcadores.
    walk.fill_umarkers()
    # Se ordenan los marcadores del pie.
    walk.sort_foot_markers()
    # Se interpolan los datos de marcadores famtantes por región.
    walk.interp_markers_positions()
    # Se almacenan el arreglo de marcadores que es el producto final de la
    # clase walk, y el fin de la exploración de video. Los cálculos de
    # cinemática suceden en su respectivo modulo, posteriormente
    walk.display(0.3)
    walk.save_markers()
>>>>>>> video
