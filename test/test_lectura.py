#!/usr/bin/env python
# coding: utf-8

'''Docstring
'''

# Copyright (C) 2016  Mariano Ramis

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

import pytest
from numpy import ndarray
from context import TESTFILES
from context import authorizedText, extractArrays
from context import extractJointMarkersArraysFromFiles

single_file_test = os.path.join(TESTFILES, 'MPlano.txt')

def test_autorizedText():
    '''Test: if the file it's the correct one, the function
    returns True value.
    '''
    assert authorizedText.evaluated(single_file_test) == True
    return

def test_extractArrays():
    '''Test: lookup the file and extract all data as a numpy array.
    '''
    array = extractArrays.textToArray(single_file_test)
    assert isinstance(array, ndarray)
    assert array.size > 0
    return

def test_processTextFiles():
    '''Test: return a dictionary with the arrays of joints
    markers as values from a filename as key.
    '''
    print single_file_test
    info = extractJointMarkersArraysFromFiles(single_file_test)
    assert isinstance(info, dict)
    return