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
import time
import pickle
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
dilate = True
roiextrapixel = 35
fpscorrection = 4
framewidth = 640
frameheight = 480
"""

config = ConfigParser()
config.read_file(StringIO(string_config))


schema = {
    "nmarkers": 7,
    "mxroi": [2, 2, 3],
    "slices": [[0, 2], [2, 4], [4, 7]],
    "mlabels": ["M0", "M1", "M2", "M3", "M4", "M5", "M6"],
    "segments": {"tight": ["M1", "M2"], "leg": ["M3", "M4"], "foot": ["M5", "M6"]},
    "joints": ["hip", "knee", "ankle"]}


path = '/home/mariano/Devel/masmarcha/test/testdata/VID_20180814_172232987.mp4'

def test_video():
    # Creación del objeto Video
    vidobj = video.Video(path, config)
    # El objeto cv2 de video.
    vid = vidobj.vid
    del(vidobj)
    # Se comprueba que se haya cerrado el objeto de video cv2
    assert(vid.isOpened() is False)

    # Comenzamos nuevamente con la creación del objeto y ahora probamos
    # los métodos relacionados con preview
    vidobj = video.Video(path, config)
    # Se hace la lectura de un frame.
    ret, pos, frame = vidobj.read_frame()
    assert(ret)
    n, contours = vidobj.find_markers(frame)
    assert(n == 0)

    # Se salta un segundo en el video.
    vidobj.jump_foward()
    ret, pos, frame = vidobj.read_frame()
    assert(ret)
    n, contours = vidobj.find_markers(frame)
    assert(n != 0)

    markers = vidobj.calculate_center_markers(contours)
    assert(isinstance(markers, np.ndarray))

    # Se prueba el metodo de visualizar el adelanto.
    vidobj.preview(0.3)
    del(vidobj)

    # Ahora probamos todo el proceso completo de extracción de marcadores en
    # el video.
    vidobj = video.Video(path, config)
    # Se calibra la cámara si hay archivo previo de calibración.
    assert(vidobj.calibration is False)
    vidobj.load_calibration_params()
    assert(vidobj.calibration)

    # Se buscan las caminatas dentro del video.
    vidobj.find_walks()

    # se guarda una de las caminatas para el test.
    walk = vidobj.walks[1]
    walkpath = os.path.join(config.get('paths', 'session'), str(walk))
    with open(walkpath, 'wb') as fh:
        pickle.dump(walk.__dict__, fh, protocol=pickle.HIGHEST_PROTOCOL)


def test_walk():

    def load():
        """Función para cargar los datos de caminata de disco."""
        walk = video.Walk(*range(4))

        walkpath = os.path.join(config.get('paths', 'session'), 'W0')
        with open(walkpath, 'rb') as fh:
            walkdata = pickle.load(fh)
        for key in walkdata.keys():
            walk.__dict__.update(walkdata)
        return(walk)


    # Se inicializa el objeto caminata con datos arbitrarios, porque se van a
    # cargar desde disco los valores verdaderos resultado de la exploración de
    # video.
    walk = load()
    assert(walk.source == path)

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
    M0 = walk.markers

    # Finalmente este proceso de arreglar los marcadores se puede resumir en
    # uno:
    del(walk)
    walk = load()
    M1 = walk.get_markers()
    element = np.random.randint(0, M0.size)

    assert(M0.flatten()[element] == M1.flatten()[element])
