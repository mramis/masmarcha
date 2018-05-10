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
from os import curdir, path

import numpy as np

syspath.append(path.join(curdir, 'src'))

import representation


def test_joint_plot():
    joint = 'cadera'
    X = np.arange(100)

    data = []
    nsesiones = 3
    for i in np.random.randint(3, 10, nsesiones):
        session = []
        for j in xrange(i):
            # Se genera una muestra de cinemática angular.
            session.append(np.array((X + np.random.normal(0, 5.), np.sin(X))))
        data.append(session)

    # metadata para agregar para cada curva de sesión.
    meta = [['20-20-20', 'Mariano', 'Izq', '', ''],
            ['20-20-20', 'Mariano', 'Izq', 'botox', ''],
            ['20-20-20', 'Mariano', 'Izq', 'ferula 32a', '']]

    # Se prueba la función con datos aleatorios de tres sesiones.
    representation.basic_joint_plot(joint, data, meta)

    mean = np.exp(-X)
    std = (np.cos(X)-np.sin(X))*10
    # Se le agregan valores medios sin alteración clínica.
    representation.basic_joint_plot(joint, data, meta, (mean, std, 100))

    # Se excede el tamaño de la muestra de sesiones (>10) para que se dibujen
    # más de un gráfico.
    meta = meta * 4  # se van a pasar 12 sesiones.
    nsesiones = 9  # ya hay tres sesiones en data.
    for i in np.random.randint(3, 10, nsesiones):
        session = []
        for j in xrange(i):
            # Se genera una muestra de cinemática angular.
            session.append(np.array((X + np.random.normal(0, 5.), np.sin(X))))
        data.append(session)

    representation.basic_joint_plot(joint, data, meta, (mean, std, 100))
