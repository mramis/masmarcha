#!/usr/bin/env python3
# coding: utf-8

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

import os

# las rutas de la aplicación.
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CORE_DIR))
CONFIGFILE = os.path.join(ROOT_DIR, "masmarcha.config")
DATABASEFILE = os.path.join(ROOT_DIR, "masmarcha.sqlite")

# Las rutas del usuario (Linux, Windows).
HOME_DIR = os.getenv("HOME", os.getenv("USERPROFILE", None))
APPLICATION_DIR = os.path.join(HOME_DIR, "masmarcha")
SESSIONS_DIR = os.path.join(APPLICATION_DIR, "sesiones")

if HOME_DIR is None:
    raise Exception(
    "ERROR: NO EXISTE EN 'PATH' RUTA DE USUARIO (HOME or USERPROFILE).")

paths = {
    "app": APPLICATION_DIR,
    "config": CONFIGFILE,
    "database": DATABASEFILE,
    "home": HOME_DIR,
    "sessions": SESSIONS_DIR
}

# Se crea el directorio de la aplicación.
if not os.path.isdir(APPLICATION_DIR):
    os.mkdir(APPLICATION_DIR)

# Se crea la carpeta de la sesiones.
if not os.path.isdir(SESSIONS_DIR):
    os.mkdir(SESSIONS_DIR)


# Configuración.
DEFAULTCONFIG = """
[session]
source =

[video]
delay = 0
endframe = 0
startframe = 0
framewidth = 640
frameheight = 480
extensions = mp4-avi

[explorer]
dilate = False
threshold = 240
clearwalks = True
emptyframelimit = 0

[walk]
maxsize = 3000
roiwidth = 125
roiheight = 35

[camera]
fps = 60
fpscorrection = 1

[kinematics]
stpsize = 6
nfixed = 100
maxcycles = 50
anglessize = 100
leftlength = 0.28
rightlength = 0.28
cyclemarker.1 = M5
cyclemarker.2 = M6
leftthreshold = 3.2
rightthreshold = 3.2
filter_by_duration = False

[plots]
dpi = 80
textsize = 16
titlesize = 23
chartwidth = 8
chartheight = 5
tablewidth = 12
tableheight = 5
subtitlesize = 18
standardeviation = 2
cell_index_width = 0.3
cell_normal_width = 0.25
"""

# El esquema de marcadores:
SCHEMA = {
    "n": 7,
    "r": 3,
    "leg": [3, 4],
    "foot": [5, 6],
    "tight": [1, 2],
    "markersxroi": [2, 2, 3],
}
