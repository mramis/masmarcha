#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2019  Mariano Ramis

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

from .settings import app_config
from .video import Walk  # posteriormente Walk va a estar en su propio modulo.


# Los valores de configuración que no cambian dentro de la sessión.
NMARKERS = app_config.getint("schema", "n")


class Explorer(object):

    def __init__(self, config):
        # NOTE: hay que ver si no se quita config cuando desarrolla la caminata.
        self.config = config
        self.source = None
        self.walks = []

    def newWalk(self):
        u"""El método inicia una nueva caminata."""
        walk = Walk(len(self.walks), self.config)
        self.walks.append(walk)
        return walk

    def findWalks(self, video):
        u"""Encuentra las caminatas dentro de un video."""
        self.walks.clear()
        walking = False
        zerocount = 0
        emptyframelimit = app_config.getint("walk", "emptyframelimit")
        while True:
            ret, pos, frame = video.read_frame()
            if not ret:
                break
            n, contours = video.contours(frame)
            centers = video.centers(contours)
            fullschema = (n == NMARKERS)
            if not walking:
                if fullschema:
                    walk = self.newWalk()
                    walk.append_centers(pos, fullschema, centers)
                    walking = True
            else:
                if fullschema:
                    walk.append_centers(pos, fullschema, centers)
                else:
                    if n == 0:
                        zerocount += 1
                        walk.append_centers(pos, fullschema, centers)
                        if zerocount > emptyframelimit:
                            walk.append_stop()
                            walking = False
                    else:
                        walk.append_centers(pos, fullschema, centers)
                        zerocount = 0

    def reportProgress(self):
        u"""Devuelve el progreso de la exploración."""
        return self.video.currentframe / self.video.videosize

    def preview(self, delay):
        u"""Vista previa del video."""
        try:
            raise DeprecationWarning("En la nueva versión no depende mas de %" % self)
        except:
            self.video.view("preview", delay)

    def walkview(self, walk, delay):
        u"""Vista de la caminata ya procesada."""
        try:
            raise DeprecationWarning("En la nueva versión no depende mas de %" % self)
        except:
            self.video.view("walk", delay, walk)
