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
    cadera=(-30, 50),
    rodilla=(-30, 90),
    tobillo=(-40, 30)
)


def basic_joint_plot(joint_name, joint_data, joint_meta, sac=None):
    u"""."""
    data_lenght = len(joint_data)
    if data_lenght > 10:
        # Si la cantidad de sesiones es mayor a 10, para que la tabla que
        # contiene la metadata no ocupe mas superficie que el gráfico, se
        # recortan los datos en listas de diez.
        if data_lenght % 10 == 0:
            n_plots = data_lenght / 10
        else:
            n_plots = data_lenght / 10 + 1
        # Aquí se produce la recursión de la función de dibujo.
        i = 0
        for j in xrange(n_plots):
            basic_joint_plot('%s_%d' % (joint_name, j+1),
                             joint_data[i: (j+1)*10],
                             joint_meta[i: (j+1)*10],
                             sac)
            i += (j+1)*10
        return

    # NOTE: esto se tiene que agregar a la configuración.
    psize = (10, 7)
    dpi = 80

    fig = plt.figure(figsize=psize, dpi=dpi)
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

    plt.show()  # Cambiar por plt.savefig()
    plt.close()
