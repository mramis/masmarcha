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


from string import ascii_uppercase

import numpy as np
import pandas as pd


class Kinematic(object):
    u"""Cinemática.

    El objeto cinemática produce y contiene los parámetros cinemáticos
    de marcha del video.
    :param name: nombre del análisis cinemático.
    :type name: str
    :param fps: cuadros por segundo del video.
    :type fps: float
    :param cmreference: !!!!!!!!!!!!!!!!!
    :type cmreference: tuple
    :param trayectories: conjunto de trayectorias del video.
    :type trayectories: list
    """

    def __init__(self, hikes):
        self._hikes = hikes
        self._split_hikes()

    def get_joint(self, joint, lat, summary=True):
        u"""Obtener angulos articulares.

        Devuelve los valores articulares de una articulación de un hemicuerpo.
        :param joint: nombre de la articualción, se espera: hit, knee, ankle.
        :type joint: str
        :param lat: hemicuerpo, se espera: right, left.
        :type lat: str
        :param summary: Si es True (por defecto), el método devuelve la
        media y el desvio estándar de los valores. En caso contrario, el método
        devuelve cada uno de los valores por ciclo.
        :type summary: bool
        :return: valores angulares.
        :rtype: np.ndarray
        """
        pass

    def get_strides(self, lat, summary=True):
        u"""Obtener zancadas.

        Devuelve el valor de la zancada según el hemicuerpo que se solicite.
        :param lat: hemicuerpo, se espera: right, left.
        :type lat: str
        :param summary: Si es True (por defecto), el método devuelve la
        media y el desvío estándar de los valores. En caso contrario, el método
        devuelve cada uno de los valores por ciclo.
        :type summary: bool
        :return: valores de zancada.
        :rtype: np.ndarray
        """
        pass

    def get_times(self, lat, summary=True):
        u"""Obtener tiempos.

        Devuelve el valor de los tiempos de ciclo del hemicuerpo que se
         solicite.
        :param lat: hemicuerpo, se espera: right, left.
        :type lat: str
        :param summary: Si es True (por defecto), el método devuelve la
        media y el desvío estándar de los valores. En caso contrario, el método
        devuelve cada uno de los valores por ciclo.
        :type summary: bool
        :return: valores de tiempo en orden: total de ciclo, fase de apoyo,
        fase de balanceo.
        :rtype: np.ndarray
        """
        pass

    def get_phases(self, lat):
        u"""Obtener Fases.

        Devuelve el porcentaje de fase de ciclo del hemicuerpo que se solicite.
        :param lat: hemicuerpo, se espera: right, left.
        :type lat: str
        :return: valores de resumen(media) de fase en orden: apoyo, balanceo
        :rtype: tuple
        """
        pass

    def get_cadency(self):
        u"""Obtener cadencia.

        Devuelve la cadencia media de la marcha. La unidad pasos
        por minuto.
        """
        pass

    def get_velocity(self):
        u"""Obtener velocidad

        Devuelve la velocidad media de la marcha. Unidad metros por segundo.
        """
        pass

    def _split_hikes(self):
        u"""Obtiene los datos de las caminatas.

        Se procesan los datos cinemáticos de las caminatas.
        """
        ljoints = []
        rjoints = []
        lspatiotemp = []
        rspatiotemp = []
        for i, hike in enumerate(self._hikes):
            code = ascii_uppercase[i]
            hike.joints_definition()
            if hike.direction < 0:
                ljoints.append(hike.joints_as_dataframe(code))
                lspatiotemp.append(hike.spatiotemporal_as_dataframe(code))
            elif hike.direction > 0:
                rjoints.append(hike.joints_as_dataframe(code))
                rspatiotemp.append(hike.spatiotemporal_as_dataframe(code))

        # NOTE: articulaciones.
        ljoints = pd.concat(ljoints).reorder_levels(['joint', 'cycle'])
        rjoints = pd.concat(rjoints).reorder_levels(['joint', 'cycle'])
        self.dfjoints = pd.concat(
            {'left': ljoints, 'right': rjoints},
            names=['side', 'joint', 'cycle']
        )
        self.dfjoints.sort_index(inplace=True)

        # NOTE: parámetros espaciotemporales.
        lspatiotemp = pd.concat(lspatiotemp, axis=1)
        rspatiotemp = pd.concat(rspatiotemp, axis=1)
        self.spaciotemporal = pd.concat(
            {'left': lspatiotemp, 'right': rspatiotemp},
            axis=1
        )
