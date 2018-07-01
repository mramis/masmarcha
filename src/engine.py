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
import json
from collections import namedtuple

from .kinoveaext import read_file, reorder_by_frames
from .kinematics import gait_cycler
from .video import find_walks, explore_walk

class Engine(object):
    u"""El motor principal del procesamiento.

    Esta clase se encarga del procesamiento de datos luego de que se obtuvieron
    a través de la lectura por parte de los motores KinoveaTrayectoriesEngine
    y VideoEngine.
    """

    walks = []
    cycles = []

    def __init__(self, userconfig):
        self.config = userconfig
        self.schema = json.load(open(userconfig.get('engine', 'schema')))

    def explore_walks(self):
        """Explora las caminatas en búsqueda de ciclos de marcha."""

        if not self.walks:
            raise Exeption()
        # se leen las preferencias del usuario.
        cyclers = self.config.get('engine', 'cycle_markers').split(", ")
        threshold = self.config.getfloat('engine', 'phase_threshold')
        # se busca en cada caminata el contenido de ciclos de marcha. Cada
        # camiata almacena informcaión del proceso de ciclado en los atributos
        # diff y mov.
        for n, walk in enumerate(self.walks):
            diff, mov, cycles =  gait_cycler(
                walk.markers,
                self.schema,
                cyclers,
                threshold)
            self.walks[n] = walk._replace(cdiff=diff, cmov=mov)
            # Se almacenan los ciclos en la lista cycles del motor.
            for cycle in cycles:
                # los marcadores que se almacenan son los que están contenidos
                # entre el primer contacto y el ultimo de cada ciclo (hs0, hs1)
                hs0, __, hs1 = cycle
                c = Cycle(walk.source, cycle, walk.markers[hs0:hs1])
                self.cycles.append(c)


class KinoveaTrayectoriesEngine(Engine):
    u"""Motor de procesamiento de archivos de trayectorias de Kinovea."""

    def __init__(self, *args, **kwargs):
        super(KinoveaTrayectoriesEngine, self).__init__(*args, **kwargs)

    def search_for_walks(self, dirpath):
        u"""Busqueda de caminatas.

        Cada archivo de texto que se exporta en kinovea debe de tener una
        caminata. Si el archivo está editado correctamente entonces se espera
        que cada caminata contenga como mínimo un ciclo de marcha.

        :param dirpath: ruta al directorio que contiene los archivos de
         trayectorias.
        :type dirpath: str
        :raise: Expection si el directorio no existe.
        """
        # Si el directio no existe se lanza una excepción
        if not os.path.isdir(dirpath):
            raise Exception()
        # se listan los archivos que se encuentran en el directorio, y se
        # aceptan solo aquellos que tienen .txt como extensión.
        Walk = namedtuple(
            "Walk",
            ["source", "stype", "id", "timeserie", "markers", "cdiff", "cmov"])
        n = 0
        for filename in os.listdir(dirpath):
            if not filename.split('.')[-1] == 'txt':
                continue
            #  cada caminata es contenedor de datos.
            n += 1

            # DEBUG: Esta parte del código genera error.
            sep = self.config.get('kinoveaext', 'separator')

            # tserie es un arreglo con los valores de tiempo que tiene el
            # archivo de kinovea como primer columna.
            tserie, kmarkers = read_file(os.path.join(dirpath, filename))
            markers = reorder_by_frames(kmarkers)
            w = Walk(filename, 'K', n, tserie, markers, 0, 0)
            self.walks.append(w)


class VideoEngine(Engine):

    def __init__(self, *args, **kwargs):
        super(VideoEngine, self).__init__(*args, **kwargs)

    def search_for_walks(self, filepath):
        u"""."""
        Walk = namedtuple("Walk",
                          ["source", "stype", "id", "frames",
                           "markers", "regions", "cdiff", "cmov"])

        extra_px = self.config.getfloat('engine', 'region_extrapx')
        filename = os.path.basename(filepath)

        for n, walk in enumerate(find_walks(filepath, self.schema)):
            frames, markers, rois = explore_walk(walk, self.schema, extra_px)
            w = Walk(filename, 'V', n, frames, markers, rois, 0, 0)
            self.walks.append(w)


class Cycle(object):
    u"""Ciclo de marcha."""
    id = 0

    def __new__(cls, *args):
        # Se incrementa el indicador de cada ciclo.
        cls.id += 1
        return super(Cycle, cls).__new__(cls)

    def __init__(self, source, cycle, markers):
        """Ciclo.

        :param source: fuente del ciclo.
        :type source: str
        :param cycle: vector de contacto inicial, despegue, contacto final del
         ciclo, relativo a la caminata del que proviene.
        :type cycle: tuple
        :param markers: arreglo de marcadores delimeitado por el vector cycle.
        :type markers: np.ndarray
        """
        self.source = source
        self.cycle = cycle
        self.markers = markers
