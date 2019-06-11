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

import os
from time import sleep

import cv2
import numpy as np

from .settings import app_config as config
from .walk import Walk


NMARKERS = config.getint("schema", "n")
NREGIONS = config.getint("schema", "r")


def explore_video(video):
    u"""Encuentra las caminatas dentro de un video."""
    walking = False
    zerocount = 0
    emptyframelimit = config.getint("explorer", "emptyframelimit")
    while True:
        # Lectura de cuadro.
        ret, pos, frame = video.read()
        if not ret:
            break
        # Búsqueda de contornos (marcadores).
        n, contours = video.contours(frame)
        centers = video.centers(contours).flatten()
        # Algoritmo de decisión.
        fullschema = (n == NMARKERS)
        if not walking:
            if fullschema:
                walk = Walk(config)
                walk.insert(pos, fullschema, centers)
                walking = True
        else:
            walk.insert(pos, fullschema, centers)
            if n == 0:
                zerocount += 1
                if zerocount > emptyframelimit:
                    walk.close()
                    walking = False
                    yield walk, pos
            else:
                zerocount = 0


class Video(object):

    def __init__(self, config):
        self.capture = None
        self.config = config
        self._dilate = config.getboolean('explorer', 'dilate')
        self._threshold = config.getfloat('explorer', 'threshold')

    def __del__(self):
        if self.capture is not None and self.capture.isOpened():
            self.capture.release()
            cv2.destroyAllWindows()

    def open(self, path=0):
        """Inicializa la captura de video."""
        self.source = path
        self.capture = cv2.VideoCapture(path)
        self.fps = int(self.capture.get(cv2.CAP_PROP_FPS))
        self.size = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.config.set("session", "source", path)
        return self.capture, self.fps

    def centers(self, contours):
        u"""Obtiene los centros de los contornos como un arreglo de numpy."""
        def contour_center(contour):
            u"""Devuelve el centro del contorno."""
            x, y, w, h = cv2.boundingRect(contour)
            return x + w/2, y + h/2
        ccenters = [contour_center(c) for c in contours]
        return np.array(ccenters, dtype=np.int16)[::-1]

    def contours(self, frame):
        u"""Encuentra dentro del cuadro los contornos de los marcadores."""
        # 6 = cv2.COLOR_BGR2GRAY
        gray = cv2.cvtColor(frame, 6)
        # 0 = cv2.THRESH_BINARY
        binary = cv2.threshold(gray, self._threshold, 255., 0)[1]
        if self._dilate:
            kernel = np.ones((3, 3), np.uint8)
            binary = cv2.dilate(binary, kernel, iterations=3)
        # 0 = cv2.RETR_EXTERNAL
        # 2 = cv2.CHAIN_APPROX_SIMPLE
        contours, __ = cv2.findContours(binary, 0, 2)
        if contours is None:
            contours = [[], ]  # Parche por el cambio de version de opencv.
        return len(contours), contours

    def get_fps(self):
        u"""Devuelve el número de cuadros por segundos."""
        correction = self.config.getfloat('camera', 'fpscorrection')
        return self.fps * correction

    def read(self):
        u"""Lectura de cuadro de video."""
        ret, frame = self.capture.read()
        posframe = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
        return ret, posframe, frame

    def new_window(self, name, extra=''):
        width = self.config.getint('video', 'framewidth')
        height = self.config.getint('video', 'frameheight')
        windowname = 'View%s: %s' % (extra, name)
        cv2.namedWindow(windowname, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(windowname, width, height)
        return windowname

    def draw_n(self, frame, n):
        u"""Dibuja en la esquina superior izquierda el número de marcadores."""
        cv2.circle(frame, (100, 100), 75, (0, 0, 0), -1)
        cv2.putText(frame, str(n), (80, 115), 0, 2, (255, 255, 255), 2, 16)

    def draw_markers(self, frame, markers, colors=False):
        u"""Dibuja sobre el cuadro la posición de los marcadores."""
        if colors is False:
            colors = ((0,0,255) for __ in range(markers.shape[0]))
        else:
            markersxroi = self.config.get('schema','markersxroi').split(',')
            combination = [int(n) for n in markersxroi]
            variation = ((0, 0, 255), (0, 255, 0), (255, 0, 0))
            colors = [variation[i] for n in combination for i in range(n)]
        for m, c in zip(markers, colors):
            cv2.circle(frame, tuple(m), 10, c, -1)

    def draw_regions(self, frame, regions, condition):
        """Dibuja las regiones de marcadores sobre el cuadro"""
        color = {0: (0, 255, 0), 1: (0, 0, 255)}
        for (p0, p1), c in zip(regions, condition):
            cv2.rectangle(frame, tuple(p0), tuple(p1), color[c], 3)

    def draw_function(self, drawtype, frame, walk, pos):
        if drawtype is "preview":
            n, conts = self.contours(frame)
            self.draw_n(frame, n)
            self.draw_markers(frame, self.centers(conts))
        elif drawtype is "walk":
            markers = np.reshape(walk.markers[pos], (NMARKERS, 2))
            regions = np.reshape(walk.regions[pos], (NREGIONS, 2, 2))
            self.draw_markers(frame, markers, True)
            self.draw_regions(frame, regions, walk.interpolatedframes[pos])

    def view(self, drawtype, walk=None):
        u"""Se muestran los objetos detectados en el video."""
        win = self.new_window(self.source)
        # se establece el rango de cuadros
        stpos = self.config.getint("video", "startframe") if walk is None else walk.startframe - 1
        lspos = self.config.getint("video", "endframe") if walk is None else walk.endframe
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, stpos)
        for pos in range(lspos - stpos):
            ret, __, frame = self.read()
            # obtienen y dibujan los marcadores
            self.draw_function(drawtype, frame, walk, pos)
            cv2.imshow(win, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            sleep(self.config.getfloat("video", "delay"))
        cv2.destroyAllWindows()

    def flip_and_resize(self, frame):
        width = self.config.getint("video", "framewidth")
        height = self.config.getint("video", "frameheight")
        return width, height, cv2.flip(cv2.resize(frame, (width, height)), 0)





class Pics(Video):

    def __init__(self, *args, **kwrags):
        super().__init__(*args, **kwrags)
        self.height = 480
        self.width = 640

    @property
    def base_array(self):
        return np.zeros((self.height, self.width, 3))

    @property
    def pic_size(self):
        return (self.height, 200, 3)

    @property
    def indexes(self):
        w = self.pic_size[1]
        x0 = [(w * i + 20 * i) for i in range(3)]
        x1 = [(w * (i + 1) + 20 * i) for i in range(3)]
        return np.array((x0, x1)).transpose()

    def calc_xcenter(self, walk, pos):
        center = np.mean(walk.markers[pos, np.arange(0, 14, 2)])
        return int(center * self.width / self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    def cut_frame(self, frame, xcenter):
        d0 = (xcenter - 100) if xcenter > 100 else 0
        d1 = (xcenter + 100)
        cutted = frame[:, d0: d1]  # HARDCORE(delta)
        if cutted.shape != self.pic_size:
            replace = np.zeros((self.pic_size))
            replace[:, :cutted.shape[1]] = cutted
            cutted = replace
        return cutted

    def frame_from_cycle(self, posframe):
        u"""Devuelve el cuadro (imagen) en la posción que se le indica."""
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, posframe)
        frame = cv2.resize(self.capture.read()[1], (self.width, self.height))
        return frame

    def build_pic(self, cframes):
        u"""Construye la imagen final con las subimágenes."""
        base = self.base_array
        for pic, (i, j) in enumerate(self.indexes):
            base[:, i: j] = cframes[pic]
        return base

    def save(self, image, name):
        destpath = os.path.join(self.config.get("current", "pics"), name)
        cv2.imwrite(u"%s.png" % destpath, image)

    def make_pics(self, cycles, walks):
        """Genera las pics de fase por cada ciclo."""
        for cycle in cycles:
            walk = walks[cycle[1]]  # walk_id
            centers = [self.calc_xcenter(walk, pos) for pos in cycle[3:]]
            frames = [self.frame_from_cycle(c) for c in cycle[3:] + walk.info[1]]  # absolute frame position
            cutted = [self.cut_frame(f, c) for f, c in zip(frames, centers)]
            pic = self.build_pic(cutted)
            self.save(pic, "W%dC%d" % (cycle[1], cycle[0]))
