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

import logging

import cv2
import numpy as np

from .settings import SCHEMA as schema
from .walkII import Walk


def contours(frame, threshold, dilate):
    u"""Encuentra dentro del cuadro los contornos de los marcadores."""
    gray = cv2.cvtColor(frame, 6)
    binary = cv2.threshold(gray, threshold, 255., 0)[1]
    if dilate:
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=5)
    contours, __ = cv2.findContours(binary, 0, 2)
    return [[], ] if contours is None else contours


def centers(contours):
    u"""Obtiene los centros de los contornos como un arreglo de numpy."""
    def contour_center(contour):
        u"""Devuelve el centro del contorno."""
        x, y, w, h = cv2.boundingRect(contour)
        return x + w/2, y + h/2
    ccenters = [contour_center(c) for c in contours]
    return len(ccenters), np.array(ccenters, dtype=np.int16)[::-1]


def colormap(n):
    u"""Generador de colores."""
    colors = [(60, 76, 231), (219, 152, 52), (113, 204, 46)]
    count = 0
    while count < n:
        c = colors.pop()
        yield c
        colors.insert(0, c)
        count += 1


def markers_colors(schema):
    u"""Colores de markadores por región."""
    return [c for n in schema["markersxroi"] for c in colormap(n)]


class Video(object):

    def __init__(self, config, schema):
        self.config = config
        self.schema = schema
        self.capture = None

    def __del__(self):
        if self.capture is not None:
            self.capture.release()

    def open(self, filepath):
        u"""Inicializa la captura de video."""
        extensions = self.config.get("video", "extensions").split("-")
        if filepath.split(".")[-1] not in extensions:
            raise Exception(u"Extensión no valiada.")

        self.capture = cv2.VideoCapture(filepath)
        self.config.set("video", "startframe", "0")
        self.config.set("video", "endframe", str(self.duration))
        return self

    @property
    def fps(self):
        if self.captue.isOpened():
            return int(self.capture.get(cv2.CAP_PROP_FPS))

    @property
    def pos(self):
        if self.capture.isOpened():
            return int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))

    @property
    def duration(self):
        if self.capture.isOpened():
            return int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def read(self):
        u"""Lectura de cuadro de video."""
        ret, framearray = self.capture.read()
        posframe = int(self.capture.get(cv2.CAP_PROP_POS_FRAMES))
        return ret, posframe, Frame(framearray, posframe, self.config)

    def setPosition(self, pos):
        u"""Establece la pocisión inicial (cuadro) de lectura de video."""
        self.capture.set(cv2.CAP_PROP_POS_FRAMES, pos)

    def searchForWalks(self):
        u"""Busca las caminatas dentro de un video."""
        VideoExplorer.restart()
        explorer = VideoExplorer(self.config)

        self.setPosition(0)
        ret, posframe, frame = self.read()
        while ret:
            nmarkers, centers = frame.getMarkersPositions()
            isfullschema = (nmarkers == self.schema["n"])
            if isfullschema is True and explorer.walking is False:
                explorer.startWalking()
            else:
                if explorer.walkGetEnd(nmarkers) is True:
                    yield posframe, explorer.walk
            explorer.walkInsert(isfullschema, posframe, centers)
            ret, posframe, frame = self.read()


class VideoExplorer(object):
    u"""Explorador de video. Busca caminatas en el mismo."""
    walk = None
    walking = False

    def __init__(self, config):
        self.config = config
        self.stopflag = StopObserver(config)

    @classmethod
    def restart(cls):
        Walk.restart()
        cls.walk = None
        cls.walking = False

    def startWalking(self):
        u"""Comienza una caminata y el proceso de agregar datos."""
        self.walk = Walk(self.config, schema)
        self.walking = True

    def walkInsert(self, *args):
        u"""Agrega datos a la caminata."""
        if self.walking:
            self.walk.insert(*args)

    def stopWalking(self):
        u"""Detiene el proceso de agregar datos a la caminata."""
        self.walk.stop()
        self.walking = False

    def walkGetEnd(self, nmarkers):
        u"""Decide el estado de la caminata."""
        if nmarkers == 0 and self.walking is True:
            return self.shouldStop()
        else:
            self.stopflag.setZero()

    def shouldStop(self):
        u"""Retorna el valor que decide si se detiene la búsqueda."""
        try:
            self.stopflag.increment()
            return False
        except Exception:
            self.stopWalking()
            return True


class StopObserver(object):
    u"""Detiene el proceso de agreagar datos a la caminata."""

    def __init__(self, config):
        self.emptycount = 0
        self.emptyframelimit = config.getint("explorer", "emptyframelimit")

    def increment(self):
        u"""Incrementa el valor de la bandera de control."""
        self.emptycount += 1
        if self.emptycount > self.emptyframelimit:
            raise Exception("Fin de la caminata.")

    def setZero(self):
        u"""Reinicia el valor de bandera."""
        self.emptycount = 0


class Frame(object):

    def __init__(self, frame, position, config):
        self._frame = frame
        self.config = config
        self.position = position
        self.width = None
        self.height = None

    @property
    def frame(self):
        return self._frame

    def getMarkersPositions(self):
        u"""Devuelve los marcadores que encontro en el cuadro."""
        dilate = self.config.getboolean("explorer", "dilate")
        threshold = self.config.getint("explorer", "threshold")
        return centers(contours(self._frame, threshold, dilate))

    def drawMarkers(self, markers, colors=[]):
        u"""Dibuja sobre el cuadro la posición de los marcadores."""
        if colors == []:
            colors = ((0,0,255) for __ in range(markers.shape[0]))
        for m, c in zip(markers, colors):
            cv2.circle(self._frame, tuple(m), 10, c, -1)

    def drawRegions(self, regions, condition):
        u"""Dibuja las regiones de marcadores sobre el cuadro"""
        cmap = tuple(colormap(3))
        color = {0: cmap[0], 1: cmap[2]}
        for (p0, p1), c in zip(regions, condition):
            cv2.rectangle(self._frame, tuple(p0), tuple(p1), color[c], 3)

    def drawText(self, n):
        u"""Escribe un mensaje en el video."""
        # NOTE: por ahora queda como la antigua versión.
        def draw_n(frame, n):
            u"""Dibuja en la esquina superior izquierda el número de marcadores."""
            cv2.circle(self._frame, (100, 100), 75, (0, 0, 0), -1)
            cv2.putText(self._frame, str(n), (80, 115), 0, 2, (255, 255, 255), 2, 16)
        draw_n(self._frame, n)

    def resize(self):
        u"""Modifica el tamaño del cuadro."""
        if self.config.getboolean("video", "resize"):
            self.width = self.config.getint("video", "framewidth")
            self.height = self.config.getint("video", "frameheight")
            self._frame = cv2.resize(self._frame, (self.width, self.height))

    def vflip(self):
        u"""Volteo vertical del cuadro."""
        if self.config.getboolean("video", "flip"):
            self._frame = cv2.flip(self._frame, 0)


class View(object):

    def __init__(self, config, schema):
        self.config = config
        self.schema = schema

    def player(self, video, walk=None, cycle=None):
        u"""Generador de cuadros de video."""
        start = self.config.getint("video", "startframe")
        end = self.config.getint("video", "endframe")
        video.setPosition(start)
        for __ in range(end - start):
            ret, pos, frame = video.read()
            if not ret:
                break
            if cycle is not None:
                return NotImplemented
            elif walk is not None:
                self.drawWalkMarkers(frame, walk)
            else:
                self.drawUnidentifiedMarkers(frame)
            frame.resize()
            frame.vflip()
            yield frame

    def drawUnidentifiedMarkers(self, frame):
        u"""Dibuja los marcadores sin identificar sobre el cuadro."""
        n, markers = frame.getMarkersPositions()
        frame.drawText(n)
        frame.drawMarkers(markers)
        return frame

    def drawWalkMarkers(self, frame, walk):
        u"""Dibuja los marcadores identificados y las regiones sobre el cuadro."""
        try:
            pos = walk.getStartPos(frame.position)
            markers = np.reshape(walk.markersView[pos], (self.schema["n"], 2))
            regions = np.reshape(walk.regionsView[pos], (self.schema["r"], 2, 2))
            frame.drawMarkers(markers, markers_colors(self.schema))
            frame.drawRegions(regions, walk.interpolation_indicators[int(pos)])
        except ValueError:
            mssg = "Caminata fuera de cuadro."
            logging.warning(mssg)
        return frame

    def drawCycleMarkers(self, frame, cycle):
        return NotImplemented
