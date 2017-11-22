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
import json

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

SCHEMAS = {
    "schema-4": {
        "name": "schema-4",
        "ix_groups": [0, 1, 2],
        "num_markers": [1, 1, 2],
        "ft_group": 2,
        "ank_marker": 0,  # BUG
        "ft_order": [0, 1],  # NOTE: para que?
        "dir_mode": 0,
        "ft_mov_markers": [0, 1],
        "markers_codenames": [["tr"], ["fi"], ["ti", "pa"]],  # BUG
        "kv_slice": [[0, 1], [1, 2], [2, 4]],
        "segments": ["tight", "leg", "foot"],
        "tight": ["fi", "tr"],
        "leg": ["ti", "fi"],
        "foot": ["pa", "ti"],
        "joints": ["hip", "knee", "ankle"]
    },
    "schema-7": {
        "ix_groups": [0, 1, 2],
        "num_markers": [2, 2, 3],
        "ft_group": 2,
        "ank_marker": 2,
        "ft_order": [0, 1, 2],  # NOTE: para que?
        "dir_mode": 0,
        "ft_mov_markers": [0, 1],
        "markers_codenames": [["fs", "tr"], ["ts", "fi"], ["pa", "pp", "ti"]],
        "kv_slice": [[0, 2], [2, 4], [4, 7]],
        "segments": ["tight", "leg", "foot"],
        "tight": ["fi", "fs"],
        "leg": ["ti", "ts"],
        "foot": ["pa", "pp"],
        "joints": ["hip", "knee", "ankle"]
    }
}

if __name__ == '__main__':
    for path in sorted(DIRS.values()):
        os.mkdir(path)
    for schema, options in SCHEMAS.iteritems():
        with open(os.path.join(DIRS['schemas'], schema + '.json'), 'w') as fh:
            json.dump(options, fh, indent=2)
