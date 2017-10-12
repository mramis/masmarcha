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

from video.proccess import px_to_m


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

    def __init__(self, hikes, metric_ref, fps):
        self._hikes = hikes
        self.stride = {'right': [], 'left': []}
        self.tcycles = {'right': [], 'left': []}
        self.tstand = {'right': [], 'left': []}
        self.tswing = {'right': [], 'left': []}
        self._split_hikes(metric_ref, fps)
        self._nrights = len(self.joints['right']['hip'])
        self._nlefts = len(self.joints['left']['hip'])

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
        array = np.array(self.joints[lat][joint])
        if summary:
            array = np.array((array.mean(axis=0), array.std(axis=0)))
        return array

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
        array = np.array(self.long_stride[lat])
        if summary:
            array = np.array((array.mean(axis=0), array.std(axis=0)))
        return array

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
        array = np.array((self.tmcycles[lat],
                          self.tmstand[lat],
                          self.tmswing[lat]))
        if summary:
            array = np.array((array.mean(axis=1), array.std(axis=1))).T
        return array

    def get_phases(self, lat):
        u"""Obtener Fases.

        Devuelve el porcentaje de fase de ciclo del hemicuerpo que se solicite.
        :param lat: hemicuerpo, se espera: right, left.
        :type lat: str
        :return: valores de resumen(media) de fase en orden: apoyo, balanceo
        :rtype: tuple
        """
        tt, ap, bal = self.get_times(lat)[:, 0]
        return round(ap / tt, 2)*100,  round(bal / tt, 2)*100

    def get_cadency(self):
        u"""Obtener cadencia.

        Devuelve la cadencia media de la marcha. La unidad pasos
        por minuto.
        """
        cd = ((120 / self.get_times('right')[0][0])
              (120 / self.get_times('left')[0][0]))
        return round(cd / 2)

    def get_velocity(self):
        u"""Obtener velocidad

        Devuelve la velocidad media de la marcha. Unidad metros por segundo.
        """
        vl = ((self.get_strides('right')[0] / self.get_times('right')[0][0] / 100) +
              (self.get_strides('left')[0] / self.get_times('left')[0][0] / 100))
        return round(vl / 2, 2)

    def _split_hikes(self, metric_ref, fps):
        u"""Obtiene los datos de las caminatas.

        Se procesan los datos cinemáticos de las caminatas.
        """
        ljoints = []
        rjoints = []
        for i, hike in enumerate(self._hikes):
            # NOTE: articulaciones.
            hike.joints_definition()
            if hike.direction < 0:
                ljoints.append(hike.joints_as_dataframe(ascii_uppercase[i]))
            elif hike.direction > 0:
                rjoints.append(hike.joints_as_dataframe(ascii_uppercase[i]))

            # # NOTE: distancias y tiempos.
            # for ihs, to, ehs in hike.cycles:
            #     X0 = hike._fixed_groups[2][ihs][1]
            #     X1 = hike._fixed_groups[2][ehs][1]
            #     px_distance = np.linalg.norm(X0 - X1)
            #     stride = self.stride[self._lat[hike.direction]]
            #     stride.append(px_to_m(px_distance, metric_ref))
            #     timecycle = self.tcycles[self._lat[hike.direction]]
            #     timecycle.append((ehs - ihs) / fps)
            #     timestand = self.tstand[self._lat[hike.direction]]
            #     timestand.append((to - ihs) / fps)
            #     timeswing = self.tswing[self._lat[hike.direction]]
            #     timeswing.append((ehs - to) / fps)

        ljoints = pd.concat(ljoints).reorder_index(['joint', 'cycle'])
        rjoints = pd.concat(rjoints).reorder_index(['joint', 'cycle'])
        self.dfjoints = pd.concat({'left': ljoints, 'right': rjoints})
