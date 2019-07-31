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

from src.core.array import *

def test_field_parser():
    print()
    value = FieldParser(WALKFIELDS).get(["markers", "x"])
    print(value)

def test_constructor():
    print()
    constructor = Constructor(WALKSHAPE)
    array = constructor.build()
    print(constructor.array.shape)

    constructor.resize()
    print(constructor.array.shape)
    assert(array.size == constructor.array.size)


def test_insertion_row():
    print()
    constructor = Constructor(WALKSHAPE)
    insertion_row = InsertionRow(constructor)

    insertion_row.increment()
    print(constructor.array.shape)

    insertion_row.index = 298
    insertion_row.increment()
    print(constructor.array.shape)


def test_inserter():
    print()
    constructor = Constructor(WALKSHAPE)
    fieldsparser = FieldParser(WALKFIELDS)
    inserter = Inserter(constructor, fieldsparser)

    explorer_output_1 = (
        234, # frame position
        True, # full schema information
        np.arange(14), # contours centers of markers
    )

    inserter.insert(*explorer_output_1)
    print(constructor.array[0])

    explorer_output_2 = (
        235, # frame position
        False, # full schema information
        np.arange(0), # No contours centers of markers
    )

    inserter.insert(*explorer_output_2)
    print(constructor.array[1])

    explorer_output_3 = (
        236, # frame position
        False, # full schema information
        np.arange(8), # few contours centers of markers
    )

    inserter.insert(*explorer_output_3)
    print(constructor.array[2])

    explorer_output_4 = (
        235, # frame position
        False, # full schema information
        np.arange(18), # many contours centers of markers
    )

    inserter.insert(*explorer_output_4)
    print(constructor.array[3])

    explorer_output_5 = (
        236, # frame position
        False, # full schema information
        np.arange(100), # a lot of contours centers of markers
    )

    inserter.insert(*explorer_output_5)
    print(constructor.array[4])


def test_walk_array():
    print()
    array = WalkArray()

    explorer_output_1 = (
        234, # frame position
        True, # full schema information
        np.arange(14), # contours centers of markers
    )
    array.addFrameData(explorer_output_1)

    markertrack = array.getView("markers region0 m1".split())
    assert(np.shares_memory(array.constructor.array, markertrack))
    array.save()
