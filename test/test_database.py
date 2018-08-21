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

from sys import path as syspath
from os import curdir, path, remove
from datetime import date

import numpy as np

syspath.append(path.join(curdir, 'src'))

import database

dbpath = path.join(curdir, 'test', 'DATABASE.db')


def test_creating_database():
    database.create(dbpath)


def test_insert_database():
    person = ('32391104', 'Ramis', 'Mariano', '32', 'Masculino', '182', 'sac')
    session = (date.today(), None, None, None)
    cycles = range(10)
    param1 = ('L',) + tuple(np.random.random(6).tolist()) + tuple(np.random.random((3, 101)))
    param2 = ('R',) + tuple(np.random.random(6).tolist()) + tuple(np.random.random((3, 101)))
    param3 = ('L',) + tuple(np.random.random(6).tolist()) + tuple(np.random.random((3, 101)))
    param4 = ('R',) + tuple(np.random.random(6).tolist()) + tuple(np.random.random((3, 101)))
    kinematics = (param1, param2, param3, param4)
    database.insert(dbpath, person, session, kinematics)


def test_search_database():

    fields = dict(name=u'', lastname=u'', age='', dx=u'sac',
                  assistance=u'', test=u'')
    meta, data = database.search(dbpath, **fields)
    assert len(meta) == 1
    assert len(data) == 4

    fields = dict(name=u'', lastname=u'', age='25-35', dx=u'',
                  assistance=u'', test=u'')
    meta, data = database.search(dbpath, **fields)
    assert len(meta) == 1
    assert len(data) == 4

    fields = dict(name=u'', lastname=u'', age='', dx=u'',
                  assistance=u'', test=u'')
    database.search(dbpath, **fields)


def test_remove_database():
    remove(dbpath)
