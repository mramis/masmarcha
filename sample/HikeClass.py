# coding: utf-8

from itertools import product

import numpy as np
import pandas as pd


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
# NOTE: La nueva clase Hike (antigua clase Trayectoria), solo se encarga de
# recibir los datos de los marcadores, de agruparlos correctamente, y de
# corregir la falta de datos. El trabajo de establecer los ciclos los va a
# realizar la clase Kinematic.

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
                        markers.append(np.random.random((nm, 2)))
                filled_groups[group] = markers
                markers = []
            self._filled_groups = filled_groups

    def split_into_dataframe(self, wich_groups, ret=False):
        u"""."""
        markers_group = {
            'filled': self._filled_groups,
            'fixed': self._fixed_groups
        }

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
        return pd.DataFrame(dataframe, index=ix)


#     def fix_in(self):
#         u"""Arregla del conjunto de marcadores de la trayectoria.

#         Ordena los marcadores de la región de tobillo. Interpola
#         (lineal) los datos faltantes.
#         """
#         if self._fixed:
#             return
#         self._direction = set_direction(self._frames[2])
#         self._frames[2] = [sort_foot_markers(X, self._direction) for X in self._frames[2]]
#         for group in (0, 1, 2):
#             indexes = self._to_interpolate[group]
#             if indexes:
#                 for ai, bi in interval([i for i, b in indexes if b is True]):
#                     ai -= self.start_frame
#                     bi -= self.start_frame
#                     dt = (bi - ai) - 1
#                     A = self._frames[group][ai]
#                     B = self._frames[group][bi]
#                     for j, arr in zip(xrange(ai + 1, bi), interpolate(A, B, dt)):
#                         self._frames[group][j] = arr
#         self._fixed = True

#     def cycle_definition(self, fps, level=0.1):
#         u"""Definición de ciclo.

#         Se establecen los ciclos, si los hay, dentro de la trayectoria. Establece
#         los atributos: cycles, phases, footmov.
#         :param fps: cuadros por segundo.
#         :type fps: float
#         :param level: umbral de velocidad para determinar cuando el pié esta en
#         movimiento.
#         :type level: float
#         """
#         # primer proceso. Se detecta la situacion de apoyo y balanceo
#         vel = []
#         lmov = []
#         for i in (0, 1):
#             mov = diff([X[i][1] for X in self._frames[2]], 1/fps)
#             vel.append(mov)
#             lmov.append(mov)
#             limit = max(vel[i]) * level  # DEBUG(HARDCORE): umbral de velocidad aceptado.
#             vel[i] = [abs(x) > limit for x in vel[i]]
#             homogenize(vel[i])
#         phases = [not (x + y) < 2 for x, y in zip(vel[0], vel[1])]

#         # segundo proceso. Se detectan ciclos dentro del trayecto.
#         st = []  # stance
#         cycles = []
#         for i, (prev, nextt) in enumerate(zip(phases[:-1], phases[1:])):
#             if prev and not nextt:  # (prev:balanceo/nextt:apoyo)
#                 st.append(i+1)
#             if nextt and not prev: # (prev:apoyo/nextt:balanceo)
#                 tf = i+1  # toeoff
#             if len(st) == 2:
#                 ret, cycle = mov_validation(lmov, ((st[0], tf-1), (tf, st[1]-1)))
#                 if ret:
#                     cycles.append(cycle)
#                 st = [st[-1]]
#         self._footmov = lmov
#         self._phases = phases
#         self._cycles = cycles
#         self._cycled = True

#     def get_joints(self):
#         u"""Calcula los angulos articulares dentro de cada ciclo en la trayectoria."""
#         for i, cycle in enumerate(self._cycles):
#             (ihs, ho),(to, ehs) = cycle
#             markers = {}
#             codenames = (('c', 'fs'), ('ts', 'fi'), ('pa', 'pp', 'ti'))
#             for j in (0, 1, 2):
#                 group = np.array(self._frames[j])
#                 for k, name in enumerate(codenames[j]):
#                     markers[name] = group[ihs: ehs+1, k, :]
#             # El marcador de tronco no se está utilizando.
#             tight = markers['fi'] - markers['fs']
#             leg = markers['ti'] - markers['ts']
#             foot = markers['pp'] - markers['pa']

#             xdirection = (None, positiveX, negativeX)[self._direction]
#             hip = 90 - Angle(tight, xdirection(tight.shape[0]))
#             knee = hip + (Angle(leg, xdirection(leg.shape[0])) - 90)
#             ankle = 90 - Angle(leg, foot)
#             hip, knee, ankle = fourierfit(np.array((hip, knee, ankle)))
#             self._joints[i] = {'hip': hip, 'knee': knee, 'ankle': ankle}
