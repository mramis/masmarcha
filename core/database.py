#!/usr/bin/env python
# coding: utf-8

"""Docstring."""

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

import sqlite3
import io

import numpy as np


# Este fragmento es la solución que encontré en stackoverflow para almacenar
# arreglos numpy en las tablas sqlite.
# http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
def adapt_array(ndarray):
    out = io.BytesIO()
    np.save(out, ndarray)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(blob):
    out = io.BytesIO(blob)
    out.seek(0)
    return np.load(out)


# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("numpyarray", convert_array)


class SqliteCreator:

    def __init__(self, config):
        self.config = config
        self.database = config.get("paths", "database")

    def create(self):
        u"""Crea las tablas de la base de datos."""
        self.createVideo()

    def createVideo(self):
        u"""Crea un archivo sqlite."""
        try:
            with sqlite3.connect(self.database, detect_types=1) as conn:
                conn.execute("""
                    CREATE TABLE video(
                    id TEXT PRIMARY KEY NOT NULL,
                    date TEXT NOT NULL,
                    fduration INTERGER NOT NULL,
                    sduration REAL NOT NULL,
                    fps INTERGER NOT NULL)
                """)
        except sqlite3.OperationalError:
            pass


class SqliterInserter(SqliteCreator):

    def insertVideo(self, *kwargs):
        u"""."""
        pass
