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

import numpy as np

sys.path.insert(0, 'src')

import video

string_config = """
[paths]
calibration = test/testdata
currentcamera = test/testdata/MTOG3-Mariano.npz
session = test/testdata

[video]
thresh = 250.0
dilate = False
roiextrapixel = 35
fpscorrection = 4
framewidth = 640
frameheight = 480
chessboardwidth = 8
chessboardheight = 4
calibframerate = 10
"""

config = ConfigParser()
config.read_file(StringIO(string_config))


schema = {
    "n": 7,
    "markersxroi": {0: [0, 1], 1: [2, 3], 2: [4, 5, 6]},
    "markerlabels": ["M0", "M1", "M2", "M3", "M4", "M5", "M6"],
    "segments": {"tight": ["M1", "M2"], "leg": ["M3", "M4"], "foot": ["M5", "M6"]},
    "joints": ["hip", "knee", "ankle"]}


path = 'test/testdata/VID_20180814_172232987.mp4'

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
    assert(vi.calibration is True)
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
    walk = explorer.walks[0]
    session = config.get('paths', 'session')
    walkpath = os.path.join(session, '{}.pickle'.format(str(walk)))
    with open(walkpath, 'wb') as fh:
        pickle.dump(walk.__dict__, fh, protocol=pickle.HIGHEST_PROTOCOL)


def test_walk():
    """Se prueba la funcionalidad de la clase walk"""
    def load():
        """Función para cargar los datos de caminata de disco."""
        walk = video.Walk(*range(5))
        walkpath = os.path.join(config.get('paths', 'session'), 'W0.pickle')
        with open(walkpath, 'rb') as fh:
            walkdata = pickle.load(fh)
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
    # Se almacenan el arreglo de marcadores que es el producto final de la
    # clase walk, y el fin de la exploración de video. Los cálculos de
    # cinemática suceden en su respectivo modulo, posteriormente
    walk.display(0.1)
    walk.save_markers()
