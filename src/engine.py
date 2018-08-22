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
import logging

import numpy as np

from kinoveaext import read_file, reorder_by_frames
from video import (find_walks, explore_walk, get_fps, get_distance_scale,
                   calibrate_camera)
from kinematics import (gait_cycler, calculate_angles, resize_angles_sample,
                        fourier_fit, calculate_spatiotemporal, get_direction)
from representation import Plotter
from database import search


class Engine(object):
    u"""El motor principal del procesamiento.

    Esta clase se encarga del procesamiento de datos luego de que se obtuvieron
    a través de la lectura por parte de los motores KinoveaTrayectoriesEngine
    y VideoEngine.
    """
    walks = []
    cycles = []

    def __init__(self, userconfig, markers_schema):
        self.cfg = userconfig
        self.schema = markers_schema

    def explore_walks(self, dump=False):
        """Explora las caminatas en búsqueda de ciclos de marcha."""
        for walk in self.walks:
            self.cycles += walk.get_cycles(self.schema, self.cfg, dump)

    def plot_session(self, withlabels=False, withtext=False):
        u"""."""
        plotter = Plotter(self.cfg).auto()

        for walk in self.walks:
            plotter.add_cycler(str(walk), walk.diff, walk.mov)

        for cycle in self.cycles:
            params = cycle.calculate_parameters(self.schema, self.cfg)
            plotter.add_cycle(*params, withlabels)

        plotter.saveplots(withtext)

    def dump_session(self, instance='both'):
        u"""Serialización de la información.

        La información que se almacena es la de instancias caminatas y ciclos.
        :param instance: objeto de información obtenida, caminata y/o ciclos.
         Por defecto: ambas.
        :type instance: str
        """
        choose = {
            'both': self.walks + self.cycles,
            'walks': self.walks,
            'cycles': self.cycles
        }
        for inst in choose[instance]:
            inst.dump(self.cfg.get('paths', 'session'))

    def load_session(self, remove=False):
        u"""Deserialización de la información de la sesión."""
        choose = {
            'walk': (Walk, self.walks),
            'cycle': (Cycle, self.cycles)
        }
        dir = self.cfg.get('paths', 'session')
        listdir = os.listdir(self.cfg.get('paths', 'session'))
        for filenpz in listdir:
            filepath = os.path.join(dir, filenpz)
            inst, iid, isource, __ = filenpz.split('.')
            constructor, container = choose[inst]
            inst = constructor(isource, iid)
            inst.add_data(**dict(np.load(filepath)))
            container.append(inst)
            if remove:
                os.remove(filepath)

    def update_sac(self):
        db = self.cfg.get('paths', 'database')
        meta, sac = search(db, dx='sac')
        angles, spacetemporal = [], []
        for data in sac:
            spacetemporal.append(data[3:9])
            angles.append(data[9:])
        mean_spacetemporal = np.array(spacetemporal).mean(axis=0)
        std_spacetemporal = np.array(spacetemporal).std(axis=0)
        mean_angles = np.array(angles).mean(axis=0)
        std_angles = np.array(angles).std(axis=0)
        filepath = self.cfg.get('paths', 'sac')
        np.savez(filepath, mean_angles=mean_angles, std_angles=std_angles,
                 mean_spacetemporal=mean_spacetemporal,
                 std_spacetemporal=std_spacetemporal, nsample=len(sac),
                 npeople=len(meta))

class KinoveaTrayectoriesEngine(Engine):
    u"""Motor de procesamiento de archivos de trayectorias de Kinovea."""

    def __init__(self, *args, **kwargs):
        super(KinoveaTrayectoriesEngine, self).__init__(*args, **kwargs)
        self.markersrate = None

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
        # En algunos equipos de grabación de video (g: MOTO G3) se tiene que
        # corregir el valor de fps.
        fpscorrection = self.cfg.getfloat('video', 'fpscorrection')
        fps = get_fps(filepath) * fpscorrection

        extra_px = self.cfg.getint('engine', 'extrapixel')
        source = os.path.basename(filepath)
        calb = self.get_calibration()
        for n, walk in enumerate(find_walks(filepath, self.schema, calb)):
            ret = explore_walk(walk, self.schema, extra_px)
            if ret is None:
                logging.error('Búsqueda de caminata: %s-%d' % (source, n))
                continue
            frames, markers, rois = ret
            w = Walk('video', n)
            w.add_data(source=source, frames=frames, markers=markers,
                       regions=rois, rate=fps, pxscale=self.px_scale(markers))
            self.walks.append(w)

    def px_scale(self, markers):
        u"""."""
        sessiondata = json.load(open(self.cfg.get('paths', 'sessiondata')))
        return(get_distance_scale(markers, sessiondata['legdistance']))

    def calibrate_camera(self, filepath, camera):
        u"""."""
        dest = os.path.join(self.cfg.get('paths', 'calibration'), camera)
        calibrate_camera(filepath, dest, chessboard=(8, 4), rate=10)
        self.cfg.set('paths', 'currentcamera', '{}.npz'.format(dest))
        with open(self.cfg.get('paths','configure'), 'w') as fh:
            self.cfg.write(fh)
        logging.info("""Calibración sucedió con exito: {}.""".format(dest))

    def get_calibration(self):
        calbpath = self.cfg.get('paths', 'currentcamera')
        if calbpath:
            return(dict(np.load(calbpath)))
        else:
            logging.warning('No se encontró calibración de la cámara')


class Walk(object):

    def __init__(self, source, id):
        u"""Caminata.

        :param type: tipo de caminata (fuente de la extracción de datos). Los
        posibles valores son "video" y "kinovea".
        :type type: str
        :param wid: numeración de la caminata dentro del procesamiento.
        :type id: int
        """
        self.type = type
        self.id = id

    def __repr__(self):
        source = ''.join(str(self.source).split('.')) # self.source es np.array
        return 'walk.{0}.{1}'.format(self.id, source)

    def add_data(self, **kwargs):
        """Agrega información principal de caminata."""
        self.__dict__.update(kwargs)

    def dump(self, dirpath):
        u"""Escribe los datos de caminata en disco.

        :param dirpath: ruta del directorio de escritura:
        :type dirpath: str
        """
        np.savez(os.path.join(dirpath, self.__repr__()), **self.__dict__)

    def get_cycles(self, schema, cfg, dump=False):
        u"""Generador de ciclos."""
        cycles = []
        self.diff, self.mov, indexes = gait_cycler(
            self.markers, schema, (cfg.get('engine', 'cyclemarker1'),
            cfg.get('engine', 'cyclemarker2')),
            cfg.getfloat('engine', 'phasethreshold'),
            cfg.getint('engine', 'safephase'))

        direction = get_direction(self.markers, schema)
        lat = ('leftside', 'rightside')[direction]

        for n, (hs, to, hss) in enumerate(indexes):
            c = Cycle(''.join(self.__repr__().split('.')), n)
            c.add_data(lat=lat, markers=self.markers[hs:hss],
                indexes=(hs, to, hss), rate=self.rate, dir=direction,
                pxscale=self.pxscale)
            if dump:
                c.dump(cfg.get('paths', 'session'))
            else:
                cycles.append(c)
        return cycles


class Cycle(object):

    def __init__(self, walk, id):
        self.walk = walk
        self.id = id

    def __repr__(self):
        return 'cycle.{0}.{1}'.format(self.id, self.walk)

    def add_data(self, **kwargs):
        """Agrega información principal de ciclo."""
        self.__dict__.update(kwargs)

    def dump(self, dirpath):
        u"""Escribe los datos de caminata en disco.

        :param dirpath: ruta del directorio de escritura:
        :type dirpath: str
        """
        np.savez(os.path.join(dirpath, self.__repr__()), **self.__dict__)

    def calculate_parameters(self, schema, cfg):
        u"""."""
        id = ''.join(str(self).split('.')) + '.' + str(self.lat)
        angles = calculate_angles(self.markers, self.dir, schema)
        if cfg.getboolean('engine', 'fitangles'):
            angles = fourier_fit(angles, 101, cfg.getint('engine', 'fourier'))
        else:
            angles = resize_angles_sample(angles, 101)
        spacetemp = calculate_spatiotemporal(
            self.indexes, self.markers, self.rate, self.pxscale)

        return(id, spacetemp, angles)

#
# class Parameters(object):
#
#     ids = []
#     angles = []
#     switch = []
#     spacetemp = []
#
#     def add_id(self, id):
#         self.ids.append(id)
#
#     def add_angles(self, angles):
#         self.angles.append(angles)
#
#     def add_switch(self, switch):
#         self.switch.append(switch)
#
#     def add_spacetemporal(self, spacetemporal):
#         self.spacetemp.append(spacetemporal)
#
#     def add(self, *parameters):
#         self.add_id(parameters[0])
#         self.add_spacetemporal(parameters[1:7])
#         self.add_angles(parameters[7:-1])
#         self.add_switch(parameters[-1])
#
#     def plot(self, cfg):
#         angles = np.array(self.angles)
#         switch = np.mean(self.switch)
#         for n, joint in enumerate(('Cadera', 'Rodilla', 'Tobillo')):
#             joint_plot(cfg, joint, angles[:, n], switch)
