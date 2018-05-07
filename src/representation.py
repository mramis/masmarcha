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


from string import capitalize
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy as np

style.use('seaborn')

COLORMAP = plt.cm.get_cmap('tab10').colors

TABASICS = dict(
    loc='center',
    cellLoc='left',
    colLoc='left',
    colLabels=['Fecha', 'Nombre', 'Lat', 'Prueba', 'Asistencia'],
    colWidths=[0.125, 0.275, 0.1, 0.25, 0.25])

JOINTLIMITS = dict(
    hip=(-30, 50),
    knee=(-30, 90),
    ankle=(-40, 30)
)


def basic_joint_plot(joint_name, joint_data, joint_meta, meanstd=None):
    u"""."""
    # NOTE: hay que poner un límite de 10 sesiones.

    # NOTE: esto se tiene que agregar a la configuración.
    psize = (10, 7)
    dpi = 80

    fig = plt.figure(figsize=psize, dpi=dpi)
    fig.suptitle(capitalize(joint_name), fontsize=24)
    # NOTE: el hspace aumenta a medida que aumentan las sesiones.
    # fig.subplots_adjust(hspace=0.7)

    # El primero es el axes en el que se dibujan las curvas de la articulación,
    # el segundo es el de la tabla que contiene la leyenda.
    main_plot = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    meta_plot = plt.subplot2grid((3, 1), (2, 0))

    if meanstd:
        # NOTE: Hay que ver si no es mejor que la línea de la media no esté
        # encima del resto de las curvas.
        main_plot.plot(meanstd[0], color='k', linewidth=1.5)
        main_plot.fill_between(np.arange(meanstd[0].size),
                               meanstd[0]-meanstd[1],
                               meanstd[0]+meanstd[1],
                               color='k', alpha=.3)
    # Este diccionario se utiliza para la construcción de la tabla de metadata,
    # durante la construcción de las gráficas se le agregan el tamaño de la
    # muestra de sesión, y el color de la misma.
    tabcollection = defaultdict(list)
    # Se construyen las curvas de la articulación, la curva va tomando mas
    # transparencia a medida que pasan las sesiones (alpha).
    alpha = .6
    for c, session in enumerate(joint_data):
        tabcollection['rowLabels'].append(len(session))
        tabcollection['rowColours'].append(COLORMAP[c])
        for data in session:
            main_plot.plot(data[0], data[1], color=COLORMAP[c], alpha=alpha)
        alpha -= 0.04
    # Se retocan los axis, y se agrega la línea de la posición neutra.
    main_plot.axhline(0, color='k', linestyle='--', linewidth=1.0)
    main_plot.set_ylim(*JOINTLIMITS[joint_name])
    main_plot.set_ylabel(u'Grados de rotación (-extensión, +flexión)')
    main_plot.set_xlabel(u'[%] Ciclo de marcha')
    # Se termina de construir el diccionario que se utiliza en la tabla. Se,
    # agregan los valores de las celdas, y se actualiza con el diccionario que
    # contiene los valores por defecto.
    tabcollection['cellText'] = joint_meta
    tabcollection.update(TABASICS)
    # Se construye la tabla.
    meta_plot.axis('off')
    meta_plot.table(**tabcollection)

    plt.show()
    plt.close()
