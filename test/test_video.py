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

session = test/testdata

[video]
thresh = 250.0
dilate = False
roiextrapixel = 35
"""

config = ConfigParser()
config.read_file(StringIO(string_config))

schema = load(open(config.get('paths', 'schema')))


def test_frame():
    schema = load(open(config.get('paths', 'schema')))
    f = video.Frame(126, np.load('test/testdata/test_frame.npy'), schema, config)
    print('\nprint ', f)

    assert(f.is_completed())
    print('\nprint ', u'número de contornos correcto')

    markers = f.calculate_center_markers()
    print('\nprint', u'calculo de centros de marcadores correcto')

    # plt.imshow(f.frame)
    # plt.scatter(markers[:, 0], markers[:, 1], color='r')
    # plt.savefig('test/testdata/test_frame_markers')
    # print('\nprint', u'se escribio la imagen con los marcadores')
    # plt.close()

    rois = f.calculate_regions().reshape(len(schema['slices']), 2, 2)
    # print('\nprint', u'calculo de regiones de interes correcto')
    # plt.imshow(f.frame)
    # plt.scatter(rois[0, :, 0], rois[0, :, 1], color='r')
    # plt.scatter(rois[1, :, 0], rois[1, :, 1], color='g')
    # plt.scatter(rois[2, :, 0], rois[2, :, 1], color='b')
    # plt.savefig('test/testdata/test_frame_rois')
    # print('\nprint', u'se escribio la imagen con las regiones')
    # plt.close()
    f.markers = f.markers[4:]
    print(f.fill_markers())


# def test_video():
#     path = '/home/mariano/Devel/masmarcha/test/testdata/VID_20180814_172232987.mp4'
#     # Se crea el objeto
#     v = video.Video(path, config)
#     # Se le da posición al cuadro para que haya marcadores en escena.
#     v.vid.set(video.cv2.CAP_PROP_POS_FRAMES, 99)
#     # se hace una lectura del cuadro.
#     __, pos1, frame1 = v.read_frame()
#     assert(pos1 == 100)
#     assert(isinstance(frame1, np.ndarray))
#     # se setean los atributos de la camara calibrada.
#     assert(v.calibration is False)
#     v.load_calibration_params()
#     assert(v.calibration is True)
#     # se posiciona 100 nuevamentes.
#     v.vid.set(video.cv2.CAP_PROP_POS_FRAMES, 99)
#     __, pos2, frame2 = v.read_frame()
#     equals = frame1.flatten() == frame2.flatten()
#     assert(any(equals))
#     assert(not all(equals))
#     # Exploración del video.
#     v.explore()
#     # Escribo en disco la caminata para test
#     v.walks[0].dump()
#

# def test_walk():
#     # # para cargar una caminata no es necesario introducir id y source.
#     # walk = video.Walk(None, 0, config)
#     # walk.load('/home/mariano/Devel/masmarcha/test/testdata/walk.0.npz')
#     # walk.classify_frames()
#     # del(walk)
#
#     # walk = video.Walk(None, 0, config)
#     # walk.load('/home/mariano/Devel/masmarcha/test/testdata/walk.0.npz')
#     # walk.calculate_uframes_rois()
#     # walk.display(pausetime=.05)
#     # del(walk)
#
#     walk = video.Walk(None, 0, config)
#     walk.load('/home/mariano/Devel/masmarcha/test/testdata/walk.0.npz')
#     walk.calculate_uframes_rois()
#     walk.detect_missing_markers()
