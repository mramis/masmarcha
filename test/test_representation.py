#!/usr/bin/env python3
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
from os import curdir, path, remove, listdir
from configparser import ConfigParser
from io import StringIO

import numpy as np

syspath.append(path.join(curdir, 'src'))

import representation


config = ConfigParser()
config.readfp(
    StringIO("""
    [paths]
    splots = %s

    [plots]
    width = 6
    height = 4
    dpi = 80
    """ % (path.join(curdir, 'test'))))


def test_joint_plot():
    joint = 'Cadera'
    X = np.linspace(-np.pi, np.pi, 101)
    angles = np.array((np.sin(X) * 10, -np.sin(X) * 10, np.tan(X) * 10))

    # Graficar tabla espaciotemporal
    plotter = representation.Plotter(config)
    table = plotter.table_plot()
    table.add_cycle(range(6))
    table.build_table()
    table.save()

    # Graficar cinemática de una articulacion
    # plotter = representation.Plotter(config)
    # ax = plotter.new_joint_plot(joint)
    # ax.add_cycle(angles[0], 65)
    # ax.save()

    # Agregar texto a un gráfico
    # plotter = representation.Plotter(config)
    # ax = plotter.new_joint_plot(joint)
    # ax.save(withtext=True)

    # # Ploteo global
    # plotter = representation.Plotter(config).auto()
    # plotter.add_cycle(['idd', [1, 65, 3], angles], withlabels=True)
    # plotter.saveplots(withtext=True)
