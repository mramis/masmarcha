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


import numpy as np


WALKSHAPE = (300, 59)

WALKFIELDS = {
    "framepos": 0,
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


class FieldParser(object):
    regions = [0, 1, 2]
    num_of_markers_columns = 14
    num_of_markers_per_region = [2, 2, 3]
    num_of_breakmarkers_columns = 28

    def __init__(self, fields):
        self.fields = fields
        self.subfield = None

    def get(self, levels):
        u"""Explora el campo hasta devolver el último de los niveles."""
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
        u"""Convierte al objeto built-in slice en un objecto built-in range."""
        return range(
            slice.start,
            slice.stop,
            slice.step if slice.step is not None else 1
        )


class Constructor(object):
    u"""Construye el arreglo y maneja los cambios de tamaño del mismo."""

    def __init__(self, shape):
        self.shape = shape
        self.array = np.zeros(shape, dtype=int)

    def build(self):
        u"""Devuelve el arreglo."""
        return self.array

    def resize(self):
        u"""Aumenta el tamaño de filas del arreglo."""
        nrows, __ = self.array.shape
        default_nrows, default_ncols = self.shape
        self.array.resize(default_nrows + nrows, default_ncols, refcheck=False)


class InsertionRow(object):
    u"""Es la fila activa durante el proceso de inserción de datos."""

    def __init__(self, constructor):
        self.constructor = constructor
        self.index = 0

    def increment(self):
        u"""Incrementa el índice de fila."""
        self.index += 1
        self.checkIndexError()

    def checkIndexError(self):
        u"""Vigila la posición del índice de fila respecto al final del arreglo."""
        if self.index == self.constructor.array.shape[0] - 1:
            self.constructor.resize()


class Inserter(object):
    u"""Inserta datos en arreglo a medida que el explorador los provee."""

    def __init__(self, constructor, fieldparser):
        self.last_fullschema_row = 0
        self.constructor = constructor
        self.fields = fieldparser
        self.row = InsertionRow(constructor)

    def insert(self, framepos, fullschema, markerscoordinates):
        u"""Inserta datos en el arreglo."""
        self.setPosition(framepos)
        self.setFullSchema(fullschema)
        self.setCoordinates(fullschema, markerscoordinates)
        self.row.increment()

    def setPosition(self, position):
        u"""Inserta el dato de posición de cuadro de video."""
        col = self.fields.get(["framepos"])
        self.constructor.array[self.row.index, col] = position

    def setFullSchema(self, fullschema):
        u"""Inserta el dato de "Esquema Completo"."""
        col = self.fields.get(["indicators", "initial"])
        self.constructor.array[self.row.index, col] = fullschema
        if fullschema:
            self.last_fullschema_row = self.row.index

    def setCoordinates(self, fullschema, markerscoordinates):
        u"""Inserta los centros de los contornos de marcadores."""
        if fullschema:
            self.setMarkers(markerscoordinates)
        else:
            self.setBreakMarkers(markerscoordinates)

    def setMarkers(self, markerscoordinates):
        u"""Inserta los centros de los contornos que cumplen con el esquema."""
        cols = self.fields.get(["markers", "all"])
        self.constructor.array[self.row.index, cols] = markerscoordinates

    def setBreakMarkers(self, markerscoordinates):
        u"""Inserta los centros de los contornos que no cumplen con el
        esquema.
        """
        size = self.fields.num_of_breakmarkers_columns
        cols = self.fields.get(["breakmarkers", "all"])
        markers = np.hstack((markerscoordinates, np.zeros(size)))
        self.constructor.array[self.row.index, cols] = markers[:size]

    def fitToLastFullSchemaRow(self):
        u"""Despues de finalizada la inserción, cierra los datos al último
        ingresado con esquema completo.
        """
        row = self.last_fullschema_row + 1
        self.constructor.array = self.constructor.array[:row]


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
