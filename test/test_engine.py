#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2018  Mariano Ramis

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
from os import curdir, path, remove, listdir
from configparser import ConfigParser
from io import StringIO

import numpy as np

syspath.append(path.join(curdir, 'src'))

import engine


config = ConfigParser()
config.readfp(
    StringIO("""

    [paths]
    database = /home/mariano/masmarcha/masmarcha.db
    sac = /home/mariano/masmarcha/sac.npz

    """))

def test_sac():
    e = engine.Engine(config, None)
    e.update_sac()
