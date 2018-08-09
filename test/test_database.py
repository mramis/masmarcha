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


global dbpath
dbpath = path.join(curdir, 'test', 'DATABASE.db')


def test_creating_database():
    database.create(dbpath)


def test_insert_database():
    kinematics = (('left', 0, 0, 0, 0, 0, 0, np.ndarray((2, 100)),
                   np.ndarray((2, 100)), np.ndarray((2, 100))),)

    person1 = (u'32391104', u'ramis', u'mariano', u'31', u'sac')
    person2 = (u'50391104', u'ramis', u'magdalena', u'20', u'sac')

    session1 = (date.today(), None, u'botox',
                u'Se coloca botox en el sóleo izquierdo')
    session2 = (date.today(), u'terapista', u'ferula', u'')

    database.insert(dbpath, person1, session1, kinematics)
    database.insert(dbpath, person1, session1, kinematics)
    database.insert(dbpath, person2, session2, kinematics)


def test_search_database():

    fields = dict(name=u'mariano', lastname=u'', age='', dx=u'',
                  assistance=u'', test=u'')
    meta, data = database.search(dbpath, **fields)
    assert len(meta) == 2
    assert len(data) == 2

    fields = dict(name=u'', lastname=u'', age='20', dx=u'',
                  assistance=u'', test=u'')
    meta, data = database.search(dbpath, **fields)
    assert len(meta) == 1
    assert len(data) == 1

    fields = dict(name=u'', lastname=u'', age='', dx=u'',
                  assistance=u'', test=u'')
    database.search(dbpath, **fields)


def test_remove_database():
    remove(dbpath)
