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

import cv2
from markers import Frame


class Video(object):
    u"""."""

    def __init__(self, filename, *args, **kwargs):
        self.video = cv2.VideoCapture(filename)
        self.set_roi()

    def get_frame(self):
        return self.video.read()

    def play(self, show_markers=False):
        u"""."""
        is_frame, frame = self.get_frame()
        while is_frame:
            if show_markers:
                markers = self.get_markers(frame)
                for mark in markers:
                    cv2.circle(frame, (mark[0], mark[1]), 7, (0, 0, 255), -1)
            cv2.imshow('video', cv2.resize(frame, None, fx=.4, fy=.4))
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
            on, frame = self.video.read()
        self.video.release()
        cv2.destroyAllWindows()

    def roi_dsg(self, array, widths=(1.2, 1.2, 1.4)):
        u"""Segmentación por defecto de las regiones de interés.

        :param array: arreglo con los centros de los marcadores.
        :type array: np.ndarray
        """
        y_cord = array[:, 1]
        top = min(y_cord)
        bottom = max(y_cord)
        distance = (bottom - top) / 6.0
        regions = []
        for seg, width in zip((1, 3, 6), widths):
            middle = (top + distance * seg)
            band_width = distance * width
            regions.append((middle - band_width, middle + band_width))
        return regions

    def get_markers(self, frame):
        u"""Obtiene los marcadores del cuadro corriente del video."""
        frame = Frame(frame, self.video.get(0))
        frame.find_markers()
        self.current_frame = frame
        return frame.markers

    def set_roi(self, *args):
        u"""Regiones donde se encuentran los marcadores.

        Establece los límites donde se espera encontrar los marcadores. Son
        tres las regiones de interés, troco: marcadores de tronco inferior y
        muslo superior, rodilla: marcadores de muslo inferior y pierna
        superior, y tobillo, marcadores de pierna inferior, pie posterior y
        pie anterior.
        """
        self.roi = False
        while not self.roi:
            markers = self.get_markers(self.get_frame()[-1])
            if len(markers) is 7:
                self.roi = self.roi_dsg(markers, *args)


if __name__ == '__main__':
    filename = '/home/mariano/Descargas/VID_20170720_132629833.mp4'
    vid = Video(filename)
    vid.play(1)
