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

import numpy as np

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

    def __init__(self, userconfig, markers_schema):
        self.config = userconfig
        self.schema = markers_schema

    def explore_walks(self):
        """Explora las caminatas en búsqueda de ciclos de marcha."""

        if not self.walks:
            raise Exeption()
        # se leen las preferencias del usuario.
        cmarker1 = self.config.get('engine', 'cyclemarker1')
        cmarker2 = self.config.get('engine', 'cyclemarker2')
        pthreshold = self.config.getfloat('engine', 'phasethreshold')

        for walk in self.walks:
            diff, mov, cycles =  gait_cycler(walk.markers, self.schema,
                                             (cmarker1, cmarker2), pthreshold)

            walk.diff = diff
            walk.mov = mov
            # Se almacenan los ciclos en la lista cycles del motor.
            for n, cycle in enumerate(cycles):
                c = Cycle(str(walk), n)
                c.add_data(cycle=cycle,
                           markers=walk.markers[cycle[0]:cycle[-1]])
                self.cycles.append(c)

    def dump_walks(self, dirpath):
        u"""Serialización de la información que se encuentra en caminatas.

        :param dirpath: directorio donde se almacenan los archivos.
        :type dirpath: str
        """
        for w in self.walks:
            w.dump(dirpath)

    def load_walks(self, dirpath):
        for wfile in os.listdir(dirpath):
            instance, wtype, wid, __ = wfile.split('.')
            if instance != 'walk':
                continue
            w = Walk(wtype, wid)
            wdata = np.load(os.path.join(dirpath, wfile))
            w.add_data(load=True, **dict(wdata))
            self.walks.append(w)


class KinoveaTrayectoriesEngine(Engine):
    u"""Motor de procesamiento de archivos de trayectorias de Kinovea."""

    def __init__(self, *args, **kwargs):
        super(KinoveaTrayectoriesEngine, self).__init__(*args, **kwargs)

    def search_for_walks(self, filepaths):
        u"""Busqueda de caminatas.

        Cada archivo de texto que se exporta en kinovea debe de tener una
        caminata. Si el archivo está editado correctamente entonces se espera
        que cada caminata contenga como mínimo un ciclo de marcha.

        :param filepaths: rutas de archivos de trayectoria.
        :type filepaths: list
        """
        # se listan los archivos que se encuentran en el directorio, y se
        # aceptan solo aquellos que tienen .txt como extensión.
        n = 0
        for source in filepaths:
            if not kfile.split('.')[-1] == 'txt':
                continue
            # tserie es un arreglo con los valores de tiempo que tiene el
            # archivo de kinovea como primer columna.
            tserie, kmarkers = read_file(kfile)
            markers = reorder_by_frames(kmarkers)
            n += 1
            w = Walk('kinovea', n)
            w.add_data(source=source, tserie=tserie, markers=markers,
                       diff=0, mov=0)
            self.walks.append(w)


class VideoEngine(Engine):

    def __init__(self, *args, **kwargs):
        super(VideoEngine, self).__init__(*args, **kwargs)

    def search_for_walks(self, filepath):
        u"""."""
        extra_px = self.config.getfloat('engine', 'extrapixel')
        source = os.path.basename(filepath)
        for n, walk in enumerate(find_walks(filepath, self.schema)):
            frames, markers, rois = explore_walk(walk, self.schema, extra_px)
            w = Walk('video', n)
            w.add_data(frames=frames, markers=markers, regions=rois,
                       diff=0, mov=0)
            self.walks.append(w)


class Walk(object):

    def __init__(self, type, id):
        u"""Caminata.

        :param wtype: tipo de caminata (fuente de la extracción de datos). Los
        posibles valores son "video" y "kinovea".
        :type type: str
        :param wid: numeración de la caminata dentro del procesamiento.
        :type id: int
        """
        self.type = type
        self.id = id

    def __repr__(self):
        return 'walk.{type}.{id}'.format(**self.__dict__)

    def add_data(self, load=False, **kwargs):
        """Agrega información principal de caminata.

        :param load: Se utiliza para modificar algunos valores cuando los datos
        que se levantan son de un archivo "npz".
        :type load: bool
        :param kwargs: argumentos con nombre que hacen a los atributos de la
        caminata: source (str), markers (np.ndarray), diff (np.ndarray), mov
        (np.ndarray), tserie (type: kinovea, np.ndarray), frames (type: video,
        np.ndarray), regions (type: video, np.ndarray)
        :type kwargs: dict
        """
        self.__dict__.update(kwargs)
        if load:
            self.__dict__['source'] = str(self.__dict__['source'])
            self.__dict__['type'] = str(self.__dict__['type'])
            self.__dict__['id'] = int(self.__dict__['id'])

    def dump(self, dirpath):
        u"""Escribe los datos de caminata en disco.

        :param dirpath: ruta del directorio de escritura:
        :type dirpath: str
        """
        np.savez(os.path.join(dirpath, self.__repr__()), **self.__dict__)


class Cycle(Walk):

    def __init__(self, walk, id):
        self.walk = walk
        self.id = id

    def __repr__(self):
        return 'cycle.{walk}.{id}'.format(**self.__dict__)

    def add_data(self, **kwargs):
        """Agrega información principal de caminata.

        :param load: Se utiliza para modificar algunos valores cuando los datos
        que se levantan son de un archivo "npz".
        :type load: bool
        :param kwargs: argumentos con nombre que hacen a los atributos del
        ciclo: xxx
        """
        super(Cycle, self).add_data(**kwargs)
