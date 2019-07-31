#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

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
import matplotlib.pyplot as plt

from src.core.walkII import Walk
from src.core.settings import config, SCHEMA as schema


config.set("walk", "roiwidth", "1")
config.set("walk", "roiheight", "1")

def test_insert():
    walk = Walk(config, schema)

    # insercción de datos.
    # well insertion.
    pos = 0
    sample = np.arange(22, 22 + 14)
    walk.insert(True, pos, sample)

    # bad insertion. lesser
    pos += 1
    sample = np.arange(22, 22 + 10)
    walk.insert(False, pos, sample)

    # bad insertion. greater
    pos += 1
    sample = np.arange(22, 22 + 18)
    walk.insert(False, pos, sample)

    assert(walk.inserter.current_row() == 3)

    # sobrepasamos el número de elemnetos esperados incialmente:
    # se pone a prueba el observador del tamaño del arreglo.
    for i in range(np.random.randint(300, 500)):
        pos += 1
        sample = np.arange(22, 22 + 14)
        walk.insert(True, pos, sample)


    # para finalizar, se completa el arreglo con cuadros incompletos.
    for i in range(100):
        pos += 1
        sample = np.arange(22, 22 + 10)
        walk.insert(False, pos, sample)


    walk.stop()
    fullschema = walk.warray._primary[:, walk.warray.fullschema_col]
    assert((np.count_nonzero(np.logical_not(fullschema))) == len(walk.warray._secondary))


def test_regions_and_markers():
    walk = Walk(config, schema)
    pos = -1

    # algnos bucles para meter información.

    for i in range(np.random.randint(30, 50)):
        pos += 1
        sample = np.arange(22, 22 + 14)
        walk.insert(True, pos, sample)

    for i in range(np.random.randint(30, 50)):
        pos += 1
        sample = np.arange(22, 22 + 10)
        walk.insert(False, pos, sample)

    for i in range(np.random.randint(30, 50)):
        pos += 1
        sample = np.arange(22, 22 + 14)
        walk.insert(True, pos, sample)

    for i in range(np.random.randint(30, 50)):
        pos += 1
        sample = np.arange(22, 22 + 10)
        walk.insert(False, pos, sample)

    for i in range(np.random.randint(30, 50)):
        pos += 1
        sample = np.arange(22, 22 + 14)
        walk.insert(True, pos, sample)

    walk.stop()

    walk.process()
