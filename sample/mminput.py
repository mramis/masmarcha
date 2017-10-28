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
# import cv2

# from video.proccess import (grouping, roi_center, image_proccess
# from video.clvideo import Trayectoria, Kinematic


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

    def read_frames(self, schema=(2, 2, 3), nomarkerstime=1.5, dref=5):
        u"""."""
        self.ty = []
        nomarkerstime *= self.fps
        last_complete_schema = 0
        refmarks = np.ndarray((0, 0))
        no_markers = 0
        M = sum(schema)
        kneeroi = None
        reading = False
        t = Trayectoria()
        for iframe in xrange(self.fcount):
            __, frame = self.vid.read()
            m, mark = image_proccess(frame)
            if mark.any():
                if m == M:
                    reading = True
                    t.start_frame = iframe
                    last_complete_schema = iframe
                    no_markers = 0
                if (not refmarks.any() and not reading) and iframe < 50:
                    if m == dref:
                        refmarks = mark
                if reading:
                    if m != M:
                        to_interp, groups = grouping(mark, schema, kneeroi)
                        t.add_frame(iframe, groups)
                        t.add_to_interpolate(iframe, to_interp)
                    else:
                        __, groups = grouping(mark, schema)
                        kneeroi = roi_center(groups[1])
                        t.add_frame(iframe, groups)
            else:
                no_markers += 1
                if reading and no_markers < nomarkerstime:
                    G0 = np.random.randint(0, 100, (2, 2))
                    G1 = np.random.randint(0, 100, (2, 2))
                    G2 = np.random.randint(0, 100, (3, 2))
                    t.add_frame(iframe, (G0, G1, G2))
                    t.add_to_interpolate(iframe, (True, True, True))
                else:
                    if reading:
                        backwards = (iframe - 1) - last_complete_schema
                        t.rm_lastNframes(backwards)
                        t.end_frame = iframe - backwards - 1
                        self.ty.append(t)
                        t = Trayectoria()
                        reading = False
        self.metricref = metric_reference(refmarks)

    def get_kinematic(self):
        u"""."""
        self.kt = Kinematic(self.name, self.fps, self.metricref, self.ty)


if __name__ == '__main__':
    pass
