# coding: utf-8

from itertools import product

import numpy as np
import pandas as pd

from video.proccess import interval, interp, homogenize


class Hike(object):
    """Conserva los datos de los marcadores de la caminata en un sentido."""

    def __init__(self):
        self.start_videoframe_position = None
        self.end_videoframe_position = None
        self.direction = None
        self._count_frames = 0
        self._groups_markers = {0: [], 1: [], 2: [], 'index_order': []}
        self._filled_groups = False
        self._fixed_groups = False
        self._to_interpolate = {0: [], 1: [], 2: []}
# NOTE: La nueva clase Hike (antigua clase Trayectoria), se encarga de recibir
# los datos de los marcadores, de agruparlos correctamente, y de corregir la
# falta de datos. El trabajo de establecer los ciclos los va a realizar la
# clase Kinematic.

    def add_markers_from_videoframe(self, index, groups):
        u"""Se agregan las trayectorias de los marcadores.

        :param index: índice del cuadro de video.
        :type index: int
        :param groups: (G0, G1, G2), arreglo de los grupos de marcadores.
        :type groups: tuple
        """
        self._count_frames += 1
        for i, g in zip((0, 1, 2), groups):
            self._groups_markers[i].append(g)
        self._groups_markers['index_order'].append(index)

    def add_index_to_interpolate(self, index, bgroups):
        u"""Se agregan indices que tienen que ser interpolados.

        :param index: índice del cuadro de video.
        :type index: int
        :param bgroups: lista de booleanos, que indica los grupos que deben ser
        interpolados.
        :type bgroups: list or tuple
        """
        self._count_frames += 1
        for i, bg in zip((0, 1, 2), bgroups):
            self._to_interpolate[i].append((index, bg))

    def rm_last_data_added(self, n):
        u"""Remueve los últimos n datos de marcadores añadidos.

        Este método se aplica al finalizar la adición de datos de marcadores.
        :param n: número de cuadros a remover.
        :type n: int
        """
        self._count_frames -= n
        while n:
            self._groups_markers[0].pop()
            self._groups_markers[1].pop()
            self._groups_markers[2].pop()
            self._groups_markers['index_order'].pop()
            self._to_interpolate[0].pop()
            self._to_interpolate[1].pop()
            self._to_interpolate[2].pop()
            n -= 1

    def get_foot_direction(self, mode=0, ret=False):
        u"""Establece la dirección del pie.

        A través del cálculo diferencial de las componentes en "y" del marcador
        de tobillo(G2) establece la velocidad de movimiento del pie. Luego
        calcula la dirección del pie cada ves que este se encuentra en estación
        de apoyo completo.
        :return: None
        """
        if self.direction:
            if ret:
                return self.direction
            else:
                return
        if not self._filled_groups:
            self.fill_groups()

        direction = 0
        arr = np.array(self._filled_groups[2])
        if mode:
            ydiff = np.diff(arr[:, 2, 1])
            for n, diff in enumerate(ydiff):
                if diff == 0:
                    XA = arr[:, 2, 0][n]
                    X0 = arr[:, 0, 0][n]
                    X1 = arr[:, 1, 0][n]
                    if abs(XA - X0) < abs(XA - X1):  # Entonces X0 es pp
                        direction += X1-X0
                    else:  # Entonces X1 es pp
                        direction += X0-X1
        else:
            X0 = arr[:, 2, 0][0]
            X1 = arr[:, 2, 0][-1]
            direction = X1 - X0
        self.direction = 1 if direction > 0 else -1
        if ret:
            return self.direction

    def fill_groups(self):
        u"""."""
        if not self._filled_groups:
            filled_groups = {}
            markers = []
            for nm, group in zip((2, 2, 3), (0, 1, 2)):
                for arr in self._groups_markers[group]:
                    if arr.shape[0] == nm:
                        markers.append(arr)
                    else:
                        markers.append(np.zeros((nm, 2)))
                filled_groups[group] = markers
                markers = []
            self._filled_groups = filled_groups

    def markers_as_dataframe(self, wich_groups, ret=False):
        u"""."""
        markers_group = {
            'filled': self._filled_groups,
            'fixed': self._fixed_groups
        }

        if wich_groups not in markers_group.keys():
            print '#mm: Bad group. Options are: filled, fixed.'
            return

        if not self._fixed_groups:
            print '#mm: Not Fixed Yet'
            wich_groups = 'filled'

        dataframe = []
        rows = product(('fs', 'tri', 'ts', 'fi', 'pa', 'pp', 'ti'), ('x', 'y'))
        ix = pd.MultiIndex.from_tuples(tuple(rows), names=['markers', 'coord'])
        for group, codes in zip((0, 1, 2), (2, 2, 3)):
            arr = np.array(markers_group[wich_groups][group])
            for i in xrange(codes):  # rows, markers, columns
                dataframe.append(arr[:, i, 0])
                dataframe.append(arr[:, i, 1])
        return pd.DataFrame(dataframe, index=ix).replace(0, np.nan)

    def cycles_as_dataframe(self):
        u"""."""
        if self._cycled:
            ncycles = self.phases.shape[1]
            ix = ('stance', 'swing')
            cl = map(
                lambda x, y: x % y,
                ('C%s', )*ncycles,
                range(1, ncycles + 1)
            )
            return pd.DataFrame(self.phases, index=ix, columns=cl)

    def fix_groups(self):
        u"""Corrige el orden de los marcadores de tobillo e interpola datos."""
        if self._fixed_groups:
            return
        if not self.direction:
            self.get_foot_direction()
        if not self._filled_groups:
            self.fill_groups()
        self._sort_foot()
        self._interpolate()

    def _sort_foot(self):
        u"""Ordena los marcadores del grupo de tobillo."""
        G2copy = np.array([arr for arr in self._filled_groups[2]])
        D0 = np.linalg.norm(G2copy[:, 2, :] - G2copy[:, 0, :], axis=1)
        D1 = np.linalg.norm(G2copy[:, 2, :] - G2copy[:, 1, :], axis=1)
        for i, mindst in enumerate(D0 < D1):
            M0, M1, M2 = G2copy[i]
            if mindst:
                G2copy[i] = np.array((M1, M0, M2))
        self._fixed_groups = self._filled_groups.copy()
        self._fixed_groups[2] = G2copy

    def _interpolate(self):
        u"""Realiza una interpolación lineal de los datos faltantes."""
        for group in (0, 1, 2):
            indexes = self._to_interpolate[group]
            if indexes:
                for ai, bi in interval([i for i, b in indexes if b is True]):
                    ai -= self.start_videoframe_position
                    bi -= self.start_videoframe_position
                    dt = (bi - ai) - 1
                    A = self._fixed_groups[group][ai]
                    B = self._fixed_groups[group][bi]
                    for j, arr in zip(xrange(ai + 1, bi), interp(A, B, dt)):
                        self._fixed_groups[group][j] = arr

    def cycle_definition(self, cycle_level=.15):
        u"""Definición de ciclo.

        Se establecen los ciclos dentro de la caminata.
        :param fps: cuadros por segundo.
        :type fps: float
        :param level: umbral de velocidad para determinar cuando el pié esta en
        movimiento.
        :type level: float
        """
        if not self._fixed_groups:
            self.fix_groups()

        mov = []
        for i in (0, 1):
            pi = np.array(self._fixed_groups[2])[:, i, :]
            pmv = np.abs(np.gradient(pi)[0].sum(axis=1))
            pmv[pmv < max(pmv)*cycle_level] = 0
            homogenize(pmv)
            mov.append(pmv)
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

        cycles = np.array(cycles)
        st = cycles[:, 1] - np.float16(cycles[:, 0])
        tt = cycles[:, 2] - np.float16(cycles[:, 0])
        self.cycles = cycles
        self.phases = np.array(((st / tt), (1 - st / tt))).round(2)
        self._cycled = True
