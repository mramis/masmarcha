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
import configparser

HOME_DIR = os.getenv("HOME", os.getenv("USERPROFILE", None))
if HOME_DIR is None:
    raise Exception(u"No se encontró $HOME or $USERPROFILE en $PATH")

APP_DIR = os.path.join(HOME_DIR, "masmarcha")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NORMAL_DIR = os.path.join(ROOT_DIR, "normal")
SESSION_DIR = os.path.join(APP_DIR, "sesiones")

CONFIG_PATH = os.path.join(APP_DIR, "application.config")

DEFAULT_CONFIG = """
[paths]
app = {APP}
normal = {NORMAL}
sourcedir = {HOME}

[explorer]
dilate = False
threshold = 240

[walk]
roiwidth = 125
roiheight = 35

[video]
delay = .1
framewidth = 640
frameheight = 480

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
cyclemarker1 = M5
cyclemarker2 = M6
leftthreshold = 3.2
rightthreshold = 3.2
filter_by_duration = False

[schema]
n = 7
r = 3
leg = 3,4
foot = 5,6
tight = 1,2
markersxroi = 0,1/2,3/4,5,6
order_segments = tight,leg,foot
order_joints = hip,knee,ankle

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

# Se crea el directorio de la aplicación.
if not os.path.isdir(APP_DIR):
    os.mkdir(APP_DIR)

# Se crea la carpeta de la sesiones.
if not os.path.isdir(SESSION_DIR):
    os.mkdir(SESSION_DIR)

# Se crea/carga el archivo de configuración.
app_config = configparser.ConfigParser()
if not os.path.isfile(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as fh:
        formatter = {"APP": APP_DIR, "HOME": HOME_DIR, "NORMAL": NORMAL_DIR}
        app_config.read_string(DEFAULT_CONFIG.format(**formatter))
        app_config.write(fh)
else:
    with open(CONFIG_PATH) as fh:
        app_config.read_file(fh)


def new_session(name):
    """Crea el directorio de la session."""
    destpath = os.path.join(SESSION_DIR, os.path.basename(name))
    walkpath = os.path.join(destpath, 'walks')
    if not os.path.isdir(destpath):
        os.mkdir(destpath)
        os.mkdir(walkpath)
    return destpath, walkpath
