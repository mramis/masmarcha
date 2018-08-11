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
    [engine]
    phasethreshold = 2.5

    [paths]
    splots = %s

    [plots]
    aspect = 0.65
    dpi = 100
    """ % (path.join(curdir, 'test'))))


def test_joint_plot():
    walk = 'walk0'
    diff = np.random.random((101, 2))
    mov = np.bool8(np.arange(101))
    mov[np.random.randint(0, 101, 50)] = False

    joint = 'Cadera'
    X = np.linspace(-np.pi, np.pi, 101)
    angles = np.array((np.sin(X) * 10, -np.sin(X) * 10, np.tan(X) * 10))
    spt = np.random.random(6)

    # Graficar tabla espaciotemporal
    plotter = representation.Plotter(config)
    table = plotter.new_table_plot()
    for __ in range(10):
        table.add_cycle(range(6))
    table.build_table()
    table.save()

    # Graficar tabla espaciotemporal con texto
    plotter = representation.Plotter(config)
    table = plotter.new_table_plot()
    for __ in range(10):
        table.add_cycle(range(6))
    table.build_table()
    table.save(withtext=True)

    # Graficar cinemática de una articulacion
    plotter = representation.Plotter(config)
    ax = plotter.new_joint_plot(joint)
    ax.add_cycle(angles[0], 65)
    ax.save()

    # Agregar texto a un gráfico
    plotter = representation.Plotter(config)
    ax = plotter.new_joint_plot(joint)
    ax.save(withtext=True)

    # Graficar cycler
    plotter = representation.Plotter(config)
    ax = plotter.new_cycler_plot('walk0')
    ax.plot_cycler_out(diff, mov)
    ax.save()

    # Ploteo global
    plotter = representation.Plotter(config).auto()
    plotter.add_cycle('idd', spt, angles, withlabels=True)
    plotter.add_cycler(walk, diff, mov)
    plotter.saveplots(withtext=True)
