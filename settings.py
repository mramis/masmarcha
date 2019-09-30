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
import sys
import shutil
import configparser as cp

from core.database import SqliteCreator


# Se establece el valor de la variable home según sea linux o windows
if sys.platform == "linux":
    home = "HOME"
elif sys.platform in ["win32", "cygwin"]:
    home = "USERPROFILE"


# directorios main
MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(MAIN_DIR, "config.d")


# archivos de configuración
config = cp.ConfigParser(interpolation=cp.ExtendedInterpolation())
configfile = os.path.join(CONFIG_DIR, "config.ini")
schemafile = os.path.join(CONFIG_DIR, "schema.json")

with open(configfile) as fh:
    config.read_file(fh)

if (config.get("paths", "usr") == ''):
    config.set("paths", "usr", os.environ[home])

with open(configfile, "w") as fh:
    config.write(fh)


# creación de directorios de app
if not os.path.isdir(config.get("paths", "app")):
    os.mkdir(config.get("paths", "app"))
    os.mkdir(config.get("paths", "video"))
    os.mkdir(config.get("paths", "session"))
    shutil.copy(configfile, config.get("paths", "configfile"))
    shutil.copy(schemafile, config.get("paths", "schemafile"))


# creación de las tablas de la base de datos
SqliteCreator(config).create()
