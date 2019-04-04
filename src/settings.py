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

HOME_DIR = os.getenv("HOME", os.getenv("USERPROFILE", None))
if HOME_DIR is None:
    raise Exception(u"No se encontró $HOME or $USERPROFILE en $PATH")

APP_DIR = os.path.join(HOME_DIR, "masmarcha")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NORMAL_DIR = os.path.join(ROOT_DIR, "normal")


class PathManager(object):

    def __init__(self):
        self.app = APP_DIR
        self.home = HOME_DIR
        self.normal = NORMAL_DIR
        self.sessions = os.path.join(APP_DIR, "sessions")
        self.mkappdir()

    def mkappdir(self):
        if not os.path.isdir(self.app):
            os.mkdir(self.app)
        if not os.path.isdir(self.sessions):
            os.mkdir(self.sessions)

    def new(self, name):
        destpath = os.path.join(self.sessions, os.path.basename(name))
        if not os.path.isdir(destpath):
            os.mkdir(destpath)
        return destpath
