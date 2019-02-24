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


import threading
from time import sleep

import numpy as np
import cv2


class Video(object):

    def __init__(self, config):
        self.cap = None
        self.config = config
        self._dilate = config.getboolean('explorer', 'dilate')
        self._threshold = config.getfloat('explorer', 'threshold')

    def __del__(self):
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()

    def open(self, path=0):
        """Inicializa la captura de video."""
        self.source = path
        self.cap = cv2.VideoCapture(path)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.size = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return self.cap, self.fps, self.size

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
        contours = cv2.findContours(binary, 0, 2)[1]
        return len(contours), contours

    def get_fps(self):
        u"""Devuelve el número de cuadros por segundos."""
        correction = self.config.getfloat('camera', 'fpscorrection')
        return self.fps * correction

    def read_frame(self):
        u"""Lectura de cuadro de video."""
        ret, frame = self.cap.read()
        pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return ret, pos, frame

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
        copy = markers.copy()
        copy.resize((self.config.getint('schema', 'n'), 2))
        if colors is False:
            colors = ((0,0,255) for __ in range(markers.shape[0]))
        else:
            markersxroi = self.config.get('schema','markersxroi').split('/')
            combination = [len(m.split(',')) for m in markersxroi]
            variation = ((0, 0, 255), (0, 255, 0), (255, 0, 0))
            colors = [variation[i] for com in combination for i in range(com)]
        for m, c in zip(copy, colors):
            cv2.circle(frame, tuple(m), 10, c, -1)

    def draw_regions(self, frame, regions, condition):
        """Dibuja las regiones de marcadores sobre el cuadro"""
        color = {0: (0, 255, 0), 1: (0, 0, 255)}
        sleep(any(condition)/6)
        for (p0, p1), c in zip(regions, condition):
            cv2.rectangle(frame, tuple(p0), tuple(p1), color[c], 3)

    def draw_function(self, drawtype, frame, walk, pos):
        if drawtype is "preview":
            n, conts = self.contours(frame)
            self.draw_n(frame, n)
            self.draw_markers(frame, self.centers(conts))
        elif drawtype is "walk":
            self.draw_markers(frame, walk.markers[pos], True)
            self.draw_regions(frame, walk.regions[pos], walk.arrincompleted[pos])

    def view(self, drawtype, delay=0.3, walk=None):
        u"""Se muestran los objetos detectados en el video."""
        win = self.new_window(self.source, '' if walk is None else walk.info[0])
        # se establece el rango de cuadros
        stpos = 0 if walk is None else walk.info[1] - 1
        lspos = self.size if walk is None else walk.info[2]
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, stpos)
        for pos in range(lspos - stpos):
            ret, __, frame = self.read_frame()
            # obtienen y dibujan los marcadores
            self.draw_function(drawtype, frame, walk, pos)
            cv2.imshow(win, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            sleep(delay)
        cv2.destroyAllWindows()


class Explorer(object):

    def __init__(self, config):
        self.config = config
        self.walks = []
        self.source = None

    def open_file(self, filename):
        self.walks.clear()
        self.source = filename
        self.video = Video(self.config)
        __, __, self.nframes = self.video.open(filename)

    def new_walk(self):
        u"""El método inicia una nueva caminata."""
        walk = Walk(len(self.walks), self.config)
        self.walks.append(walk)
        print('New walk', str(walk))
        return walk

    def find_walks(self, pqueue=None):
        u"""Encuentra las caminatas dentro de un video."""
        walking = False
        while True:
            ret, pos, frame = self.video.read_frame()
            if not ret:
                break
            n, conts = self.video.contours(frame)
            centers = self.video.centers(conts)
            fullschema = (n == self.config.getint('schema', 'n'))
            if not walking:
                if fullschema:
                    walk = self.new_walk()
                    walk.append_centers(pos, fullschema, centers)
                    walking = True
            else:
                walk.append_centers(pos, fullschema, centers)
                if n == 0:
                    walk.append_stop()
                    walking = False
                    if pqueue:
                        pqueue.put(pos)
                        sleep(0.00001)
        if pqueue:
            pqueue.put(pos)
            pqueue.put(-1)

    def preview(self, delay):
        self.video.view("preview", delay)

    def walkview(self, walk, delay):
        self.video.view("walk", delay, walk)


class Walk(object):
    maxsize = 2500

    def __init__(self, id, config):
        self.id = id
        self.config = config
        mplaces = config.getint('schema', 'n')
        rplaces = config.getint('schema', 'r')
        self._cols = (1, 1, mplaces*2, rplaces*4, rplaces)
        self._array = np.zeros((self.maxsize, sum(self._cols)), dtype=np.int16)
        self._currow = 0
        self._incompleted = []

    def __repr__(self):
        return 'W{0}'.format(self.id)

    @property
    def arrnrows(self):
        return np.arange(self._array.shape[0])

    @property
    def info(self):
        return (self.id, self._array[0, 0], self._array[-1, 0])

    @property
    def arrcompleted(self):
        return self._array[:, 1]

    @property
    def markersxroi(self):
        out = []
        stringtuple = self.config.get('schema', 'markersxroi')
        for tup in stringtuple.split('/'):
            stringvector = tup.split(',')
            out.append([int(x) for x in stringvector])
        return(out)

    @property
    def ixmarkers(self):
        r0, r1, r2 = self.markersxroi
        nmarkers = self.config.getint('schema', 'n')
        imks = np.arange(nmarkers) * 2 + sum(self._cols[:2])
        return imks[r0,], imks[r1,], imks[r2,]

    @property
    def iymarkers(self):
        r0, r1, r2 = self.markersxroi
        nmarkers = self.config.getint('schema', 'n')
        imks = np.arange(nmarkers) * 2 + sum(self._cols[:2]) + 1
        return imks[r0,], imks[r1,], imks[r2,]

    @property
    def imarkers(self):
        array = []
        for x, y in zip(self.ixmarkers, self.iymarkers):
            array.append(np.vstack((x, y)).transpose().flatten())
        return array

    @property

    def ixregion(self):
        r0 = np.arange(2) * 2 + sum(self._cols[:3])
        r1 = np.arange(2) * 2 + sum(self._cols[:3]) + 4
        r2 = np.arange(2) * 2 + sum(self._cols[:3]) + 8
        return r0, r1, r2

    @property

    def iyregion(self):
        r0 = np.arange(2) * 2 + sum(self._cols[:3]) + 1
        r1 = np.arange(2) * 2 + sum(self._cols[:3]) + 5
        r2 = np.arange(2) * 2 + sum(self._cols[:3]) + 9
        return r0, r1, r2

    @property
    def iincompleted(self):
        return np.arange(self.config.getint('schema','r')) + sum(self._cols[:4])

    @property
    def arrincompleted(self):
        return self._array[:, self.iincompleted]

    @property
    def regions(self):
        cols = np.arange(self._cols[3]) + sum(self._cols[:3])
        return self._array[:, cols].reshape(self._array.shape[0], 3, 2, 2)

    @property
    def markers(self):
        cols = np.arange(self._cols[2]) + sum(self._cols[:2])
        return self._array[:, cols]

    def append_centers(self, pos, fullschema, centers):
        u"""Agrega información del cuadro de video."""
        if fullschema:
            data = np.hstack((pos, fullschema, centers.flatten()))
            self._array[self._currow, np.arange(sum(self._cols[:3]))] = data
        else:
            data = (pos, fullschema)
            self._incompleted.append(centers)
            self._array[self._currow, np.arange(sum(self._cols[:2]))] = data
        self._currow += 1

    def append_stop(self):
        u"""Cierra la información de cuadros en la caminata."""
        lastcompleted = self.arrnrows[np.bool8(self.arrcompleted)][-1]
        self._array = self._array[:lastcompleted+1]

    def calculate_regions(self):
        u"""Encuentra las regiones de interes del esquema de marcadores."""
        xextra = self.config.getint('walk', 'roiwidth')
        yextra = self.config.getint('walk', 'roiheight')
        for x, rx in zip(self.ixmarkers, self.ixregion):
            _min = np.min(self._array[:, x], 1) - xextra
            _max = np.max(self._array[:, x], 1) + xextra
            self._array[:, rx] = np.vstack((_min, _max)).transpose()
        for y, ry in zip(self.iymarkers, self.iyregion):
            _min = np.min(self._array[:, y], 1) - yextra
            _max = np.max(self._array[:, y], 1) + yextra
            self._array[:, ry] = np.vstack((_min, _max)).transpose()

    def interpolate_regions(self):
        u"""Crea las regiones de interes de los cuadros incompletos"""
        comp = self.arrnrows[np.bool8(self.arrcompleted)]
        inco = self.arrnrows[np.logical_not(np.bool8(self.arrcompleted))]
        regions = np.hstack(self.ixregion), np.hstack(self.iyregion)
        for r in np.hstack(regions):
            self._array[inco, r] = np.interp(inco, comp, self._array[comp, r])

    def recover_incompleted(self):
        incompleted = []
        axis = self.arrnrows[np.logical_not(self.arrcompleted)]
        for pos, centers in zip(axis, self._incompleted):
            xm = centers[:, 0]
            ym = centers[:, 1]
            for r, (ix, iy) in enumerate(zip(self.ixregion, self.iyregion)):
                x0, x1 = self._array[pos, ix]
                x = np.logical_and(xm > x0, xm < x1)
                y0, y1 = self._array[pos, iy]
                y = np.logical_and(ym > y0, ym < y1)
                substitution = centers[np.logical_and(x, y)]
                if len(substitution) == len(self.markersxroi[r]):
                    self._array[pos, self.imarkers[r]] = substitution.flatten()
                    incompleted.append(0)
                else:
                    incompleted.append(1)
            self._array[pos, self.iincompleted] = incompleted
            incompleted.clear()

    def sort_foot(self):
        u"""ordena los marcadores de pie."""
        indexes = np.array(self.markersxroi[2])
        # El 2 es por las dos primeras columnas del arreglo
        x = 2 + indexes * 2
        y = 2 + indexes * 2 + 1

        indexes = np.array((x, y)).transpose()
        ia, ib, ic = indexes
        ma, mb, mc = [self._array[:, xy] for xy in indexes]

        segments = np.array((ma-mb, mb-mc, mc-ma))
        sequence = np.array(((ia, ib), (ib, ic), (ic, ia)))
        distances = np.linalg.norm(segments, axis=2).transpose()

        ordered_distances = np.argsort(distances)
        ordered_indexes = []
        for row in sequence[ordered_distances]:
            A, B, C = row
            ia = np.intersect1d(A, C)
            ib = np.intersect1d(A, B)
            ic = np.intersect1d(B, C)
            ordered_indexes.append(np.hstack((ia, ib, ic)))
        for r, ix in enumerate(ordered_indexes):
            self._array[r, indexes.flatten()] = self._array[r, ix]

    def interpolate_markers(self):
        for r, (mx, my) in enumerate(zip(self.ixmarkers, self.iymarkers)):
            indexes = np.bool8(self.arrincompleted[:, r])
            comp = self.arrnrows[np.logical_not(indexes)]
            inco = self.arrnrows[indexes]
            for m in np.hstack((mx, my)):
                interp = np.interp(inco, comp, self._array[comp, m])
                self._array[inco, m] = interp

    def find_markers(self):
        self.calculate_regions()
        self.interpolate_regions()
        self.recover_incompleted()
        self.sort_foot()
        self.interpolate_markers()
