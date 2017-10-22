#!/usr/bin/env python
# coding: utf-8

"""La nueva clase Hike (antigua clase Trayectoria), se encarga de recibir
los datos de los marcadores, de agruparlos correctamente, de corregir la
falta de datos, de definir los ciclos, y calcular los angulos dentro del
ciclo. Tambien los presenta como Pandas DataFrame.
"""

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


from itertools import product

import numpy as np
import pandas as pd

from video.proccess import (interval, interp, homogenize, positiveX, negativeX,
                            angle, fourierfit, px_to_m)


class Hike(object):
    """Conserva los datos de los marcadores de la caminata en un sentido."""

    def __init__(self, schema, fps, metrics):
        self.schema = schema
        self.start_videoframe_position = None
        self.end_videoframe_position = None
        self.direction = None
        self.joints = {}
        self.videofps = fps
        self.videometricsample = metrics[0]  # muestra de referencia
        self.videometricscale = metrics[1]  # escala de conversión
        self._gcluster = {g: [] for g in schema['i.groups']}
        self._gcluster['index_order'] = []
        self._to_interpolate = {g: [] for g in schema['i.groups']}
        self._filled_cluster = False
        self._fixed_cluster = False
        self._count_frames = 0
        self._cycled = None
        self._sorted = None
        self._interpolated = None

    def add_markers_from_videoframe(self, index, cluster):
        u"""Se agregan las trayectorias de los marcadores.

        :param index: índice del cuadro de video.
        :type index: int
        :param cluster: (G0, G1, G2), arreglo de los grupos de marcadores.
        :type cluster: tuple
        """
        self._count_frames += 1
        for i, g in zip(self.schema['i.groups'], cluster):
            self._gcluster[i].append(g)
        self._gcluster['index_order'].append(index)

    def add_index_to_interpolate(self, index, bcluster):
        u"""Se agregan indices de cuadros a interpolar.

        :param index: índice del cuadro de video.
        :type index: int
        :param bcluster: lista de booleanos, que indica los grupos que deben
        ser interpolados.
        :type bcluster: list or tuple
        """
        self._count_frames += 1
        for i, bg in zip(self.schema['i.groups'], bcluster):
            self._to_interpolate[i].append((index, bg))

    def rm_last_added_data(self, n):
        u"""Remueve los últimos n datos de marcadores añadidos.

        Este método se aplica al finalizar la adición de datos de marcadores.
        :param n: número de cuadros a remover.
        :type n: int
        """
        self._count_frames -= n
        while n:
            for i in self.schema['i.groups']:
                self._gcluster[i].pop()
                self._to_interpolate[i].pop()
            self._gcluster['index_order'].pop()
            n -= 1

    def fill_groups(self):
        u"""Rellenar grupos.

        Este método toma cada conjunto de marcadores por cuadro, y cada grupo
        por conjunto. Entonces revisa que el número de marcadores que existe en
        el conjunto sea igual al número esperado *según el esquema*. Si no lo
        es, reemplaza el grupo de marcadores por un arreglo de ceros, con la
        misma dimensión que la esperada.
        Cabe mencionar que el tipo de arreglo de grupo es un arreglo de Numpy.
        """
        if not self._filled_cluster:
            filled_cluster = {}
            markers = []
            iterable = zip(self.schema['n.markers'], self.schema['i.groups'])
            for nm, group in iterable:
                for arr in self._gcluster[group]:
                    if arr.shape[0] == nm:
                        markers.append(arr)
                    else:
                        markers.append(np.zeros((nm, 2)))
                filled_cluster[group] = np.array(markers)
                markers = []
            self._filled_cluster = filled_cluster

    def get_direction(self, force_mod=False):
        u"""Establece la dirección de la caminata.

        A través del cálculo diferencial de las componentes en "y" del marcador
        de tobillo(G2) establece la velocidad de movimiento del pie. Luego
        calcula la dirección del pie cada ves que este se encuentra en estación
        de apoyo completo.
        :return: None
        """
        if not self.direction:
            mod = self.schema['d.mod']
            if force_mod:
                mod = force_mod
            self.fill_cluster()
            self.sort_foot()

            direction = 0
            arr = self._filled_cluster[self.schema['gr.foot']]
            if mod:
                ydiff = np.diff(arr[:, self.schema['mk.ankle'], 1])
                ffoot, rfoot, __ = self.schema['or.foot']
                for n, diff in enumerate(ydiff):
                    if diff == 0:
                        X1 = arr[:, rfoot, 0][n]
                        X0 = arr[:, ffoot, 0][n]
                        direction += X1 - X0
            else:
                X0 = arr[:, 0, 0][0]
                X1 = arr[:, 0, 0][-1]
                direction = X1 - X0

            self.direction = 1 if direction > 0 else -1

    def sort_foot(self):
        u"""Ordena los marcadores del grupo de tobillo."""
        if self.schema['sort_foot'] and not self._sorted:
            foot_group = self._filled_cluster[self.schema['gr.foot']].copy()
            ffoot, rfoot, ankle = self.schema['or.foot']
            ankle_rfoot = foot_group[:, ankle, :] - foot_group[:, rfoot, :]
            ankle_ffoot = foot_group[:, ankle, :] - foot_group[:, ffoot, :]
            d0 = np.linalg.norm(ankle_rfoot, axis=1)
            d1 = np.linalg.norm(ankle_ffoot, axis=1)
            for i, mindst in enumerate(d0 < d1):
                m0, m1, m2 = foot_group[i]
                if mindst:
                    foot_group[i] = np.array((m1, m0, m2))
            self._fixed_cluster = self._filled_cluster.copy()
            self._fixed_cluster[self.schema['gr.foot']] = foot_group
            self._sorted = True

    def interpolate(self):
        u"""Realiza una interpolación lineal de los datos faltantes."""
        if self.schema['interpolate'] and not self._interpolated:
            for group in self.schema['i.groups']:
                indexes = self._to_interpolate[group]
                if indexes:
                    frames = [i for i, b in indexes if b is True]
                    for ai, bi in interval(frames):
                        ai -= self.start_videoframe_position
                        bi -= self.start_videoframe_position
                        dt = (bi - ai) - 1
                        A = self._fixed_cluster[group][ai]
                        B = self._fixed_cluster[group][bi]
                        for j, arr in zip(range(ai + 1, bi), interp(A, B, dt)):
                            self._fixed_cluster[group][j] = arr
            self._interpolated = True

    def fix_cluster(self):
        u"""Corrige el orden de los marcadores de tobillo e interpola datos."""
        if not self._fixed_cluster:
            self.fill_cluster()
            self.sort_foot()
            self.interpolate()

    def cycle_definition(self, cycle_level=.15):
        u"""Definición de ciclo.

        Se establecen los ciclos dentro de la caminata.
        :param fps: cuadros por segundo.
        :type fps: float
        :param level: umbral de velocidad para determinar cuando el pié esta en
        movimiento.
        :type level: float
        """
        self.fix_cluster()

        mov = []
        for i in self.schema['mk.foot']:
            pi = self._fixed_cluster[self.schema['gr.foot']][:, i, :]
            pmv = np.abs(np.gradient(pi)[0].sum(axis=1))
            pmv[pmv < max(pmv)*cycle_level] = 0
            homogenize(pmv)
            mov.append(pmv)
        self._foot_vel = mov
        mov = np.array(mov).sum(axis=0)
        mov[mov > 0] = 1
        self._foot_mov = mov

        st = []  # stance
        cycles = []
        for i, (pr, nx) in enumerate(zip(mov[:-1], mov[1:])):
            if pr and not nx:
                st.append(i+1)
            if not pr and nx:
                tf = i+1  # toeoff
            if len(st) == 2:
                cycles.append((st[0], tf, st[1]))
                st = [st[1]]

        if cycles:
            cycles = np.array(cycles)
            # NOTE: Parámetros espaciotemporales. Zancada y tiempos.
            ihs, to, ehs = cycles.transpose()
            ankle = self.schema['mk.ankle']
            X0 = self._fixed_cluster[self.schema['gr.foot']][ihs, ankle, :]
            X1 = self._fixed_cluster[self.schema['gr.foot']][ehs, ankle, :]
            self.pxstride = np.linalg.norm(X0 - X1, axis=1)
            self.stride = px_to_m(self.pxstride,
                                  self.videometricsample,
                                  self.videometricscale)
            times_array = np.array(
                ((ehs - ihs), (to - ihs), (ehs - to)), dtype='float'
            )
            self.times = times_array / self.videofps
            self.phases = self.times[1:] / self.times[0]
            self.cycles = cycles
            self.ncycles = len(cycles)
            self._cycled = True
        else:
            print u"#mm: No cycles in hike."
            self.cycles = None

    def joints_definition(self):
        u"""."""

        self.fix_cluster()
        self.cycle_definition()
        if not self.cycles:
            return

        for i, cycle in enumerate(self.cycles):
            ihs, to, ehs = cycle
            markers = {}
            for j in self.schema['i.groups']:
                for k, name in enumerate(self.schema['mk.codenames'][j]):
                    markers[name] = self._fixed_cluster[j][ihs: ehs+1, k, :]
            segments = {}
            for segment in self.schema['or.segments']:
                key = 'sg.%s' % segment
                a, b = self.schema[key]
                segments[segment] = markers[a] - markers[b]

            if not self.direction:
                self.get_direction()

            joints = Joints(self.schema, segments, self.direction)
            self.joints[i] = joints.fit()

    def markers_as_dataframe(self, wich_cluster='fixed'):
        u"""."""
        markers_group = {
            'filled': self._filled_cluster,
            'fixed': self._fixed_cluster
        }
        if wich_cluster not in markers_group.keys():
            print '#mm: Bad group. Options are: filled, fixed.'
            return

        self.fill_cluster()
        self.fix_cluster()
        df = []
        markers_name = reduce(lambda x, y: x + y, self.schema['mk.codenames'])
        rows = (markers_name, ('x', 'y'))
        ix = pd.MultiIndex.from_product(rows, names=['markers', 'coord'])
        iterable = zip(self.schema['i.groups'], self.schema['n.markers'])
        for group, codes in iterable:
            arr = np.array(markers_group[wich_cluster][group])
            for i in xrange(codes):
                df.append(arr[:, i, 0])
                df.append(arr[:, i, 1])
        return pd.DataFrame(df, index=ix, dtype='int').replace(0, np.nan)

    def joints_as_dataframe(self, code=''):
        u"""."""
        if self._cycled:
            dataframe = []
            codecycles = [code + str(i) for i in xrange(self.ncycles)]
            joints = self.schema['or.joints']
            ix = pd.MultiIndex.from_product(
                (codecycles, joints),
                names=('cycle', 'joint')
            )
            for cycle in self.joints:
                for joint in joints:
                    dataframe.append(self.joints[cycle][joint])
            return pd.DataFrame(dataframe, index=ix)
        else:
            print '#mm: not cycled yet'

    def spatiotemporal_as_dataframe(self, code=''):
        u"""."""
        if self._cycled:
            codecycles = [code + str(i) for i in xrange(self.ncycles)]
            ix = ('stride lenght', 'cycle time', 'stance time', 'swing time',
                  'stance phase', 'swing phase', 'velocity [m/s]', 'cadence')

            dataframe = np.vstack((self.stride,
                                   self.times,
                                   self.phases,
                                   self.stride / self.times[0],
                                   120 / self.times[0]
                                   ))
            return pd.DataFrame(dataframe, index=ix, columns=codecycles)
        else:
            print '#mm: not cycled yet'


class Joints(object):

    def __init__(self, schema, segments, direction):
        self.schema = schema
        self.segments = segments
        self.xcanonical = (None, positiveX, negativeX)
        self.direction = direction
        self.joints = {j: None for j in schema['or.joints']}

    def get_hip(self):
        if not self.joints['hip']:
            canonical = self.xcanonical[self.direction]
            tight = self.segments['tight']
            self.joints['hip'] = 90 - angle(tight, canonical(tight.shape[0]))
        return self.joints['hip']

    def get_knee(self):
        if not self.joints['knee']:
            canonical = self.xcanonical[self.direction]
            leg = self.segments['leg']
            if not self.hip:
                hip = self.get_hip()
            self.joints['knee'] = hip + angle(leg, canonical(leg.shape[0])) - 90
        return self.joints['knee']

    def get_ankle(self):
        if not self.joints['ankle']:
            leg = self.segments['leg']
            foot = self.segments['foot']
            self.joints['ankle'] = 90 - angle(leg, foot)
        return self.joints['ankle']

    def fit(self):
        method = {
            'hip': "self.get_hip()",
            'knee': "self.get_knee()",
            'ankle': "self.get_ankle()",
        }
        joints = self.schema['or.joints']
        to_fit = [eval(method[joint]) for joint in joints]
        self.joints = {j: f for j, f in zip(joints, fourierfit(to_fit))}
        return self.joints
