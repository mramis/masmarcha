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

import matplotlib.pyplot as plt
import matplotlib.style as style
from collections import defaultdict


style.use('seaborn')

COLORMAP = plt.cm.get_cmap('tab10').colors

TABASICS = dict(
    loc='center',
    cellLoc='left',
    colLoc='left',
    colLabels=['Fecha', 'Nombre', 'Lat', 'Prueba', 'Asistencia'],
    colWidths=[0.1, 0.3, 0.1, 0.25, 0.25]
)


def basic_joint_plot(joint_name, joint_data, joint_meta, psize=(10, 7)):
    u"""."""

    # Note: hay que poner un límite de 10 sesiones.

    # La figura por defecto tiene las dimensiones psize, y una resolución de
    # 80 pixeles por pulgada, el título corresponde al nombre de la
    # articulación.
    # NOTE: Se tiene que ajustar el h_space a la cantidad de sessiones que se
    # dibujan.
    fig = plt.figure(figsize=psize, dpi=80)
    fig.suptitle(joint_name)
    fig.subplots_adjust(hspace=0.7)  # NOTE: (*)

    # EL primer sublot es el gráfico de la cinemática, y el segundo es la tabla
    # con los datos del entorno de marcha (metadata)
    main_plot = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
    meta_plot = plt.subplot2grid((3, 1), (2, 0))

    # Este diccionario es el que se utiliza para construir las filas de la
    # tabla. En la iteración se agregan los datos de la cantidad de ciclos que
    # tiene cada sesión y el color con la que se dibuja la misma.
    tabcollection = defaultdict(list)

    # Se dibujan las curvas de la cinemática de la articulación.
    for c, data in enumerate(joint_data):
        main_plot.plot(data, color=COLORMAP[c])
        tabcollection['rowColours'].append(COLORMAP[c])
        tabcollection['rowLabels'].append(len(data))

    # NOTE: Continuar desde acá con los detalles del subplot de cinemática.
    main_plot.axhline(0, color='k', linestyle='--', linewidth=1.0)
    main_plot.set_ylabel(u'Extensión    Flexión')
    main_plot.set_xlabel(u'% Ciclo de marcha')

    # Se agregan a la tabla los valores que completan las celdas, estos datos
    # deben estár ordenados como lo están los datos de cinemática. Además se
    # actualiza con los valores basicos.
    tabcollection['cellText'] = joint_meta
    tabcollection.update(TABASICS)

    # Se dibuja la tabla.
    meta_plot.axis('off')
    meta_plot.table(**tabcollection)

    plt.show()
