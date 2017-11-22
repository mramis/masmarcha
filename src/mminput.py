#!/usr/bin/env python
# coding: utf-8

"""Módulo para la extracción de información de los archivos de exportación del
software Kinovea.
"""

# Copyright (C) 2016  Mariano Ramis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np
import cv2

from process import image_process, grouping, roi_center
from HikeClass import Hike
from KinematicClass import Kinematic


class KinoveaFile(object):
    u"""Lectura de los archivos de texto que exporta kinovea."""

    def __init__(self, path, schema):
        self.fps = None
        self.schema = schema
        self._gcluster = {g: [] for g in schema['i.groups']}
        with open(path) as fh:
            self._file = fh.read().replace(',', '.')
        self._split_data()

    def _split_data(self):
        u"""."""
        # se extraen los datos de texto.
        toten = u'0:00:00:00'
        duration = None
        marker = []
        groups = []
        kf_list = self._file.split('\r\n')
        while kf_list:
            line = kf_list.pop(0).rstrip()
            if marker and line:
                marker.append(line.split()[1:])
                if not duration:
                    duration = self._time_format(line.split()[0])
            if not line:
                if marker:
                    if not self.fps:
                        self.fps = len(marker) / duration
                    groups.append(np.array(marker, dtype='float'))
                    marker = []
            elif line.startswith(toten):
                marker.append(line.split()[1:])
        # los marcadores se agrupan en un diccionario (se lo lleva a la forma
        # que admite la clase Hike los grupos de marcadores).
        for g, (i, j) in zip(self.schema['i.groups'], self.schema['kv.order']):
            for row in xrange(groups[0].shape[0]):
                self._gcluster[g].append(np.array(groups)[i:j, row, :])
            self._gcluster[g] = np.array(self._gcluster[g])

    def _time_format(self, time):
        u"""Transforma la secuencia de tiempo en punto flotante (segundos).

        :param time: Estructura de tiempo de kinovea "0:00:00:00".
        :type time: str
        """
        __, mm, ss, cc = time.split(':')
        return float(mm) * 60 + float(ss) + float(cc) / 100.


class VideoFile(object):
    u"""."""

    def __init__(self, filename):
        self.name = filename
        self.vid = cv2.VideoCapture(filename)
        self.fps = self.vid.get(cv2.CAP_PROP_FPS)
        self.fcount = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))

    def read_frames(self, schema, nomarkerstime=1.5, dref=5):
        u"""."""
        expected_markers = schema['n.markers']
        M = sum(expected_markers)
        safe_None = 1.5 * self.fps
        last_M = 0
        active = False
        count_non_data = 0
        metrics = np.zeros(())

        hikes = []
        hike, h, i = None, 0, 0
        ret, frame = self.vid.read()
        while ret:
            m, mark = image_process(frame)
            if mark.any():
                if m == M:
                    active = True
                    if not hike:
                        hike = Hike(schema, self.fps, (metrics, .3))  #!Hardcore.
                        h += 1
                        kr = None
                    if not hike.start_videoframe_position:
                        hike.start_videoframe_position = i
                    last_M = i
                    count_non_data = 0
                # NOTE:  Esta parte del código debe ser revisada.
                # Se va a cambiar la forma de calibrar la imagen.
                if (not metrics.any() and not active) and i < 50:  #!Hardcore
                    if m == dref:  #!Hardcore
                        metrics = mark
                # Fin de calibracion.
                if active:
                    # NOTE: Hay que revisar la mejor manera de agrupar los
                    # marcadores.
                    if m != M:
                        to_interp, groups = grouping(mark, expected_markers, kr)  #!Hardcore
                        hike.add_markers_from_videoframe(i, groups)
                        hike.add_index_to_interpolate(i, to_interp)
                    else:
                        __, groups = grouping(mark, expected_markers)
                        kr = roi_center(groups[1])
                        hike.add_markers_from_videoframe(i, groups)
            else:
                count_non_data += 1
                if active and count_non_data < safe_None: #!Hardcore
                    G0 = np.random.random(size=(2, 2))
                    G1 = np.random.random(size=(2, 2))
                    G2 = np.random.random(size=(3, 2))
                    hike.add_markers_from_videoframe(i, (G0, G1, G2))
                    hike.add_index_to_interpolate(i, (True, True, True))
                else:
                    if active:
                        backwards = (i - 1) - last_M
                        hike.rm_last_added_data(backwards)
                        hike.end_videoframe_position = i - backwards - 1
                        hikes.append(hike)
                        hike = None
                        active = False
            ret, frame = self.vid.read()
            i += 1

        self.kinematic = Kinematic(hikes)


if __name__ == '__main__':
    pass
