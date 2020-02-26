#!/usr/bin/env python3
# coding: utf-8

u"""Los arreglos de datos de marcha."""

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


import json
import numpy as np


WALKFIELDS = {
    "indicators": {
        "all": slice(1, 5),
        "initial": 1,
        "regions": slice(2, 5),
        "region0": 2,
        "region1": 3,
        "region2": 4,
    },
    "regions": {
        "all": slice(5, 17),
        "region0": {
            "all": slice(5, 9),
            "p0": slice(5, 7),
            "p1": slice(7, 9)
        },
        "region1": {
            "all": slice(9, 13),
            "p0": slice(9, 11),
            "p1": slice(11, 13)
        },
        "region2": {
            "all": slice(13, 17),
            "p0": slice(13, 15),
            "p1": slice(15, 17)
        }
    },
    "markers": {
        "all": slice(17, 31),
        "x": slice(17, 31, 2),
        "y": slice(18, 31, 2),
        "region0": {
            "all": slice(17, 21),
            "x": slice(17, 21, 2),
            "y": slice(18, 21, 2),
            "m0": slice(17, 19),
            "m1": slice(19, 21),
        },
        "region1": {
            "all": slice(21, 25),
            "x": slice(21, 25, 2),
            "y": slice(22, 25, 2),
            "m2": slice(21, 23),
            "m3": slice(23, 25),
        },
        "region2":{
            "all": slice(25, 31),
            "x": slice(25, 31, 2),
            "y": slice(26, 31, 2),
            "m4": slice(25, 27),
            "m5": slice(27, 29),
            "m6": slice(29, 31),
        }
    },
    "breakmarkers": {
        "all": slice(31, 59),
        "x": slice(31, 59, 2),
        "y": slice(32, 59, 2),
    }
}


class ColumnsParser:

    def __init__(self, fields):
        self.fields = fields
        self.subfield = None

    @property
    def video_columns(self):
        cols = [
            self.config.get("schema", "markers_num") * 2 +
            self.config.get("schema", "markers_ext") * 2 +
        ]
        return sum(cols), cols
        
    @property
    def walk_columns(self):
        cols [
            1 +  # posición
            1 +  # completitud de esquema
            self.config.get("schema", "regions_num") * 3 +
            self.config.get("schema", "markers_num") * 2 +
            self.config.get("schema", "markers_ext") * 2 +
            self.config.get("schema", "regions_num") * 4
        ]
        return sum(cols), cols

    def __build_level(self, level, array):
        pass




    def get(self, levels):
        """Explora el campo hasta devolver el último de los niveles."""
        field = self.fields if self.subfield is None else self.subfield
        value = field[levels.pop(0)]
        if levels == []:
            self.subfield = None
            return value
        else:
            self.subfield = value
            return self.get(levels)

    @staticmethod
    def sliceToRange(slice):
        """Convierte al objeto built-in slice en un objecto built-in range."""
        return range(
            slice.start,
            slice.stop,
            slice.step if slice.step is not None else 1
        )


class VideoArray:
    """Arreglo de datos 2D.

    Este arreglo está diseñado para almacenar los marcadores encontrados
    durante el procesamiento de video. Contiene tantas filas como cuadros
    de video, y el número de columnas está definido por la cantidad de
    marcadores que presenta el esquema.

    Arreglo General (numpy 2d array):

    [t0, x0, y0, x1, y1, x2, ... xm, ym, xm+1, ym+1, xm+2, ym+2, ..., xu, yu]
    [t1, x0, y0, x1, y1, x2, ... xm, ym, xm+1, ym+1, xm+2, ym+2, ..., xu, yu]
    [t2, x0, y0, x1, y1, x2, ... xm, ym, xm+1, ym+1, xm+2, ym+2, ..., xu, yu]
    ...
    [tf, x0, y0, x1, y1, x2, ... xm, ym, xm+1, ym+1, xm+2, ym+2, ..., xu, yu]
    
    donde, t es la marca temporal, x e y las coordenadas en el plano del
    marcador, m es el número de marcadores del esquema, y u es el número
    de marcadores extras que el usuario desea agregar.
    """

    def __init__(self, nframes, config):
        self.__row = 0
        self.config = config
        self.parser = ColumnsParser(config)
        self.__array = np.zeros((nframes, self.parser.video_columns), int)

    def __repr__(self):
        return f"General Markers array {self.__array.shape}"

    @property
    def view(self):
        """Devuelve un acceso al arreglo principal."""
        return self.__array.view()

    @property
    def index(self):
        """Devuelve una arreglo de índices de fila del arreglo principal."""
        nrows, __ = self.__array.shape
        return np.arange(nrows)

    def insert(self, markers):
        """Agrega elementos al arreglo principal."""
        m = len(markers)
        ncols = min(m, self.paser.video_columns)
        self.__array[self.__row, ncols] = markers[:ncols]
        self.__row += 1

    def nonzero(self):
        """Devuelve un arreglo con los índices de fila que no son cero.
        :return: arreglo 1d.
        """
        rows, __ = np.nonzero(self.__array)
        return np.unique(rows)

    def fullschema(self):
        """Devuelve un arreglo de índices de fila que son de esquema completo.
        """
        n = self.config.getint("schema", "markers_num")
        rows = np.sum(np.not_equal(self.__array, 0), axis=1)
        return self.index[np.equal(rows, n * 2)]


class WalkArray:

    def __init__(self, config):
        self.config = config
        self.parser = FieldParser(config)
        self.__array = None

    def build(self, video_subarray):
        nrows, __ = video_subarray.shape
        self.__array = np.zeros((nrows, self.parser.walk_columns), dtype=int)
        return self



class WalkArray(object):
    u"""El arreglo de caminata. Contiene las trayectorias de los marcadores."""

    def __init__(self):
        self.constructor = Constructor(WALKSHAPE)
        self.fieldsparser = FieldParser(WALKFIELDS)
        self.datainserter = Inserter(self.constructor, self.fieldsparser)

    @property
    def array(self):
        return self.constructor.array

    @property
    def nrows(self):
        return self.array.shape[0]

    @property
    def direction(self):
        field = self.fieldsparser.get(["markers", "region0", "m0"])
        direction = self.array[-1, field] - self.array[0, field]
        return np.sign(direction)[0]  # X coord

    def addFrameData(self, frame_data):
        u"""inserta los datos del cuadro de video en el arreglo."""
        self.datainserter.insert(*frame_data)

    def close(self):
        u"""Cierra el arreglo de datos."""
        self.datainserter.fitToLastFullSchemaRow()

    def getView(self, field_section):
        u"""Devuelve numpy.view de las columnas de la sección del arreglo."""
        field = self.fieldsparser.get(field_section)
        return self.array[:, field]

    def save(self):
        u"""Guarda el arreglo en disco (npz, sqlite, hdf5, ...)."""
        return NotImplemented
