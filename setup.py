#!/usr/bin/env python3
# coding: utf-8

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

import os

APP = os.path.join(os.environ['HOME'], 'masmarcha')
SESSION = os.path.join(APP, 'session')
SPLOTS = os.path.join(APP, 'splots')
CAPTURES = os.path.join(APP, 'captures')
INI = os.path.join(APP, 'masmarcha.ini')
SCHEMA = os.path.join(APP, 'schema7.json')

default_config = """
[engine]
fourierfit = 4
extrapixel = 35
cyclemarker1 = M5
cyclemarker2 = M6
phasethreshold = 2.5
safephase = 10
markersrate = 0
pixelscale = 0
meterdistance = 0.3

[paths]
configure = {APP}/masmarcha.ini
database = {APP}/masmarcha.db
schema = {APP}/schema7.json
session = {APP}/session
splots = {APP}/splots
captures = {APP}/captures

[kinovea]
separator = \,n

[video]
binarythreshold = 250.0
framewidth = 640
frameheight = 480
fpscorrection = 1

[plots]
width = 6
height = 4
dpi = 100
"""

default_schema = """
{
"schema": [2, 2, 3],
"slices": [[0, 2], [2, 4], [4, 7]],
"codes": ["M0", "M1", "M2", "M3", "M4", "M5", "M6"],
"segments": {"tight": ["M1", "M2"], "leg": ["M3", "M4"], "foot": ["M5", "M6"]},
"joints": ["hip", "knee", "ankle"]
}
"""

def check_paths():
    u"""Inspecciona las rutas de la apliacionself.

    Por defecto crea las carpetas y rutas que se necesitan para correr la
    aplicación.
    """
    if not os.path.isdir(APP):
        os.mkdir(APP)
    if not os.path.isdir(SESSION):
        os.mkdir(SESSION)
    if not os.path.isdir(SPLOTS):
        os.mkdir(SPLOTS)
    if not os.path.isdir(CAPTURES):
        os.mkdir(CAPTURES)
    if not os.path.isfile(INI):
        with open(INI, 'w') as inifile:
            inifile.write(default_config.format(APP=APP))
    if not os.path.isfile(SCHEMA):
        with open(SCHEMA, 'w') as schemafile:
            schemafile.write(default_schema)

if __name__ == '__main__':
    check_paths()
