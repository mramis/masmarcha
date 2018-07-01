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

import numpy as np


def read_file(filename, sep='\n'):
    u"""."""
    with open(filename) as fh:
        data = fh.readlines()
    # Se separan los datos del texto en listas. La lista trayectory es la
    # que recive los datos de cada trayectoria. La lista markers es la que
    # recibe cada trayectoria.
    trayectory = []
    markers_ls = []

    header = data[0]
    assert(header.startswith('#Kinovea'))

    # Los datos de trayectorias comienzan en la tercer línea.
    for line in data[2:]:
        # kinovea tiene un caracter de escape especial, y diferente para cada
        #  plataforma. esto tiene que ser configurado por el usuario.
        if line == sep:
            if trayectory:
                markers_ls.append(trayectory)
            trayectory = []
        else:
            # en algunas plataformas kinovea entrega los puntos flotantes
            # con comas.
            trayectory.append(line.replace(',', '.').split())

    # NOTE: ACÁ VA UN ESTAMENTO DE TRY-EXCEPT, PORQUE SE VA ADMITIR EL TIEMPO
    # SOLO EN MILISEGUNDOS.
    markers = np.array(markers_ls, dtype=np.float16)
    # timeseries es la primer columna de cada uno de los arreglos de la
    # variable markers. Las otras dos son las coordenadas [x, y]
    return(markers[0, :, 0], markers[:, :, 1:])


def reorder_by_frames(markers):
    u"""."""
    # la nueva forma del arreglo de marcadores tiene el formato que se utiliza
    # en el scanner de video, un arreglo por cuadro de video. En cada uno de
    # los arreglos están los marcadores oredenados según se define en el
    # esquema.
    nmarkers, nframes, ncols = markers.shape
    new_shape = np.empty((nframes, nmarkers, ncols))
    for i in range(nmarkers):
        new_shape[:, i, :] = markers[i, :, :]

    return(new_shape)

        # # Se obtienen los ciclos dentro de la caminata, y dos arreglos mas que
        # # se utilizan para mostrar las velocidades y los cambios de fase.
        # diff, mov, cycles = gait_cycler(markers_reshape,
        #                                 self.schema,
        #                                 self.cym,
        #                                 self.pht)
        #
        # idy = '%sW1' % self.file_id
        # logger.info(u"Caminata %s - %d ciclos" % (idy, len(cycles)))
        #
        # # Se envian los resultados al motor.
        # container.append({
        #     'idy': idy,
        #     'markers': markers,
        #     'missing': None,
        #     'cycles': cycles,
        #     'diff': diff,
        #     'mov': mov
        # })
