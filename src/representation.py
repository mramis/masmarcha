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
from os import path

import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy as np

style.use('seaborn')

COLORMAP = plt.cm.get_cmap('tab20').colors

TABASICS = dict(
    loc='center',
    cellLoc='left',
    colLoc='left',
    colLabels=['Fecha', 'Nombre', 'Lat', 'Prueba', 'Asistencia'],
    colWidths=[0.125, 0.275, 0.1, 0.25, 0.25])

JOINTLIMITS = dict(
    cadera=(-30, 50),
    rodilla=(-30, 90),
    tobillo=(-40, 30)
)


def joint_plot(joint_name, joint_data, joint_meta, config, sac=None):
    u"""."""

    plt.close()
    # Cada gráfico de articulación tiene como leyenda la metadata de la sesión,
    # esto es, la fecha, el nombre, si recibió algún tipo de asistencia y/o se
    # realizó algún tipo de prueba.
    # Si la cantidad de sesiones excede a 10, entonces se produce un mecanismo
    # de recursión en el que se generan las gráficas necesarias para que en
    # cada uno de ellos haya hasta diez sesiones. Este procedimiento se
    # implementa por una cuestión estética.
    data_lenght = len(joint_data)
    nplots = data_lenght / 10 + bool(data_lenght % 10)
    if nplots > 1:
        i = 0
        for j in xrange(nplots):
            joint_plot('%s_%d' % (joint_name, j+1),
                       joint_data[i: (j+1)*10],
                       joint_meta[i: (j+1)*10],
                       config, sac)
            i += (j+1)*10
        return

    # Desde aquí el código de dibujo de curvas.

    figsize = map(int, config.get('drawparams', 'figsize').split(','))
    dpi = config.getint('drawparams', 'dpi')

    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.suptitle(capitalize(joint_name), fontsize=24)
    fig.subplots_adjust(hspace=0.12*data_lenght)

    # El primero es el axes en el que se dibujan las curvas de la articulación,
    # el segundo es el de la tabla que contiene la leyenda.
    main_plot = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    meta_plot = plt.subplot2grid((3, 1), (2, 0))

    # Este diccionario se utiliza para la construcción de la tabla de metadata,
    # durante la construcción de las gráficas se le agregan el tamaño de la
    # muestra de sesión, y el color de la misma.
    tabcollection = defaultdict(list)

    if sac:
        mean, std, nsac = sac
        # NOTE: Hay que ver si no es mejor que la línea de la media no esté
        # encima del resto de las curvas.
        main_plot.plot(mean, color='k', linewidth=1.5)
        main_plot.fill_between(np.arange(mean.size),
                               mean-std,
                               mean+std,
                               color='k', alpha=.3)
        # Se agregan a la tabla los datos de la media SAC
        tabcollection['rowLabels'].append(nsac)
        tabcollection['rowColours'].append((0., 0., 0.))
        joint_meta.insert(0, ['-', 'SAC (N=%d)' % nsac, 'izq-der', '-', '-'])

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
    main_plot.set_ylim(*JOINTLIMITS[joint_name.split('_')[0]])
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

    plt.savefig('%s.png' % path.join(config.get('paths', 'plots'), joint_name))


def spacetemporal_plot(sptemp_data, config, boxplot=False):
    u"""."""

    table_rows = [u'Muestra', u'Duración', u'Apoyo', u'Balanceo',
                  u'Zancada', u'Cadencia', u'Velocidad']

    figsize = map(int, config.get('drawparams', 'figsize').split(','))
    dpi = config.getint('drawparams', 'dpi')

    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.suptitle(u'Parámetros espacio-temporales', fontsize=24)
    fig.subplots_adjust(hspace=0.12)

    table = plt.subplot2grid((2, 6), (0, 0), colspan=6)
    table.axis('off')
    table.table(loc='center', cellLoc='center',
                colLoc='left', rowLabels=table_rows,
                cellText=sptemp_data.round(2),
                colColours=COLORMAP[:sptemp_data.shape[1]])

    if boxplot:
        for iparam in range(6):
            ax = plt.subplot2grid((2, 6), (1, iparam))
            ax.boxplot(sptemp_data[1:, iparam],
                       labels=(table_rows[1:][iparam],),
                       showmeans=True)

    plt.tight_layout()
    plt.show()
