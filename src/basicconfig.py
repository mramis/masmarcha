#!/usr/bin/env python
# coding: utf-8

"""Configuración básica de la App."""

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


ROOTPATH = os.environ['HOME']
APPPATH = os.path.join(ROOTPATH, 'masmarcha')
DIRS = {
    "app": APPPATH,
    "schemas": os.path.join(APPPATH, 'schemas'),
}
FILES = {
    "database": os.path.join(APPPATH, 'masmarcha.db')
}
PATHS = DIRS.copy()
PATHS.update(FILES)


if __name__ == '__main__':
    for path in sorted(DIRS.values()):
        os.mkdir(path)
