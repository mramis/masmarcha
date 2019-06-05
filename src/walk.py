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

import os
import logging
import numpy as np

from .settings import app_config as config

WALKMAXSIZE = config.getint("walk", "maxsize")
NINDICATORS = 5  # NOTE: Ver las primeras 5 columnas en el diagrama
NMARKERS = config.getint("schema", "n")
NREGIONS = config.getint("schema", "r")
COLITEMS = np.array((NINDICATORS, NMARKERS * 2, NREGIONS * 4))


class Walk(object):
    __counter = 0

    def __init__(self, config):
        Walk.__counter += 1
        self.id = Walk.__counter
        self.row = 0
        self.array = np.zeros((WALKMAXSIZE, COLITEMS.sum()), dtype="int16")
        self.colitems = COLITEMS
        self.insertend = COLITEMS[:2].sum()
        self.insertstart = COLITEMS[:1].sum()
        self.nofullschemaarray = []
        self.lastfullrow = 0
        self.processed = False
        logging.debug(self)

    def __str__(self):
        return "Caminata {}".format(self.id)

    @classmethod
    def num_of_walks(cls):
        return cls.__counter

    @property
    def fullschema(self):
        u"""Arreglo booleano que indica la cantidad de datos completos."""
        return np.equal(self.array[:, 1], 1)

    @property
    def markers(self):
        u"""Devuelve un "view" de las componentes de las regiones."""
        return self.array[:, COLITEMS[:1].sum(): COLITEMS[:2].sum()]

    @property
    def regions(self):
        u"""Devuelve un "view" de las componentes de las regiones."""
        return self.array[:, COLITEMS[:2].sum(): COLITEMS[:3].sum()]

    @property
    def interpolatedframes(self):
        u"""Devuelve un "view" de los cuadros interpolados."""
        return self.array[:, 2: 2 + NREGIONS]

    @property
    def dir(self):
        u"""Alias de Walk.direction."""
        return self.direction

    @property
    def direction(self):
        """Devuelve la dirección de la caminata."""
        dir = self.array[-1, self.slxmarkers] - self.array[0, self.slxmarkers]
        return -1 if np.mean(dir) < 0 else 1

    @property
    def startframe(self):
        return int(self.array[0, 0])

    @property
    def endframe(self):
        return int(self.array[-1, 0])

    def insert(self, posframe, fullschema, xymarkers):
        """Ingresa datos de la exploración del cuadro de video al arreglo."""
        self.array[self.row, 0] = posframe
        self.array[self.row, 1] = fullschema
        if fullschema:
            self.array[self.row, self.insertstart: self.insertend] = xymarkers
        else:
            self.nofullschemaarray.append(xymarkers)
        self.row += 1
        self.lastfullrow = self.row if fullschema else self.lastfullrow

    @property
    def checkfullframes(self):
        u"""Revisa la cantidad de datos completos e informa."""
        return np.count_nonzero(self.fullschema)

    def close(self):
        """Cierra el array para agregar elementos."""
        self.array = self.array[:self.lastfullrow]
        for __ in range(self.row - self.lastfullrow):
            self.nofullschemaarray.pop()

    def save(self, session=None):
        NotImplemented
        # refpath = '/{0}/walks/walk{1}'
        # if not session:
        #     session = os.path.basename(self.config.get("current", "session")).split('.')[0]
        # with h5py.File("masmarcha.hdf5", "a") as fh:
        #     fh.create_dataset(refpath.format(session, self.id), data=self.array)

    @property
    def nmxroi(self):
        u"""Número de marcadores por región de interés."""
        return np.intp(config.get("schema", "markersxroi").split(','))

    @property
    def slmarkers(self):
        u"""Generador(slice) de la subdivisión de marcadores."""
        # NOTE: donde empiezan los marcadores.
        i = COLITEMS[:1].sum()
        for mxr in self.nmxroi * 2:
            yield slice(i, i + mxr, 2), slice(i + 1, i + mxr, 2)
            i += mxr

    @property
    def slregions(self):
        u"""Generador(slice) de la subdivisión de regiones."""
        # NOTE: donde empiezan las regiones.
        i = COLITEMS[:2].sum()
        for r in range(NREGIONS):
            # NOTE: (4) componentes.
            start, stop = (i + r * 4, i + (r + 1) * 4)
            yield slice(start, stop)

    def calculateRegions(self):
        u"""Calcula las regiones de interés según el esquema de marcadores."""
        self.roiwidth = config.getint('walk', 'roiwidth')
        self.roiheight = config.getint('walk', 'roiheight')
        for (slx, sly), roi in zip(self.slmarkers, self.slregions):
            xmn = np.min(self.array[:, slx], axis=1) - self.roiwidth
            xmx = np.max(self.array[:, slx], axis=1) + self.roiwidth
            ymn = np.min(self.array[:, sly], axis=1) - self.roiheight
            ymx = np.max(self.array[:, sly], axis=1) + self.roiheight
            self.array[:, roi] = np.vstack((xmn, ymn, xmx, ymx)).transpose()
        logging.debug("%s - Regiones obtenidas" % self)

    @property
    def slregions(self):
        u"""Generador(slice) de la subdivisión de regiones."""
        i = COLITEMS[:2].sum()
        for r in range(NREGIONS):
            start, stop = (i + r * 4, i + (r + 1) * 4)
            yield slice(start, stop)

    def centerRegions(self):
        u"""Se calcula los centros de las regiones de interés."""
        def center(roi):
            u"""Calcula el centro de la región de interés."""
            xmin, ymin, xmax, ymax = roi.transpose()
            xcenter = xmin + (xmax - xmin) * .5
            ycenter = ymin + (ymax - ymin) * .5
            return (xcenter, ycenter)
        centers = [center(self.array[:, iroi]) for iroi in self.slregions]
        return np.array(centers)

    def verifyRegions(self, stdscale=3):
        u"""Verifica la posición (altura) en de los centros de las regiones."""
        ycenters = self.centerRegions()[:, 1]
        mean = np.mean(ycenters, axis=1)[:, np.newaxis]
        std = np.std(ycenters, axis=1)[:, np.newaxis]
        # Las regiones que son normales (o regulares).
        normal = np.logical_and(mean - std < ycenters, ycenters < mean + std)
        # Las regiones que no estan en el rango deben ser interpoladas.
        wrongcenters = np.logical_or(*np.logical_not(normal))
        self.array[wrongcenters, 1] = 0
        logging.debug("%s - Verificación de posición de regiones." % self)

    def interpolateRegions(self):
        u"""Crea las regiones de interes de los cuadros incompletos"""
        fs = self.fullschema
        nfs = np.logical_not(fs)
        rows = np.arange(self.array.shape[0])
        colregions = np.arange(COLITEMS[:2].sum(), COLITEMS[:3].sum())
        for colroi in colregions:
            self.array[nfs, colroi] = np.interp(
                rows[nfs], rows[fs], self.array[fs, colroi])
        logging.debug("%s - Regiones interpoladas" % self)

    @property
    def slxmarkers(self):
        u"""Devuelve un slice con las posiciones de los x-marcadores."""
        return slice(COLITEMS[:1].sum(), COLITEMS[:2].sum(), 2)

    @property
    def slymarkers(self):
        u"""Devuelve un slice con las posiciones de los y-marcadores."""
        return slice(COLITEMS[:1].sum() + 1, COLITEMS[:2].sum(), 2)

    def markersRecovery(self):
        u"""Recupera datos intercambiados de cuadros no-fullschema."""
        toreplacecol = 2
        for (xmk, ymk), roi, nm in zip(self.slmarkers, self.slregions, self.nmxroi):
            xmin, ymin, xmax, ymax = self.array[np.newaxis, :, roi].transpose()
            xmarkers = self.array[:, self.slxmarkers]
            ymarkers = self.array[:, self.slymarkers]
            xfound = np.logical_and(xmin < xmarkers, xmarkers < xmax)
            yfound = np.logical_and(ymin < ymarkers, ymarkers < ymax)
            # Coordenadas que coinsiden tanto en x como en y.
            matched = np.logical_and(xfound, yfound)
            rightcount = np.equal(np.count_nonzero(matched, axis=1), nm)
            # los valores a reemplazar que cumplen con las coincidencias.
            xreplace = xmarkers[rightcount][matched[rightcount]]
            yreplace = ymarkers[rightcount][matched[rightcount]]
            nrows = np.count_nonzero(rightcount)
            self.array[rightcount, xmk] = xreplace.reshape(nrows, nm)
            self.array[rightcount, ymk] = yreplace.reshape(nrows, nm)
            # Se coloca en la columna de indicadores la región a interpolar.
            self.array[:, toreplacecol] = np.logical_not(rightcount)
            toreplacecol += 1
        logging.debug("%s - Datos recuperados" % self)

    def sortingFoot1(self):
        u"""ordena los marcadores de pie según la dirección marcha."""
        m5 = self.markers[:, -4: -2].copy()
        m6 = self.markers[:, -2:].copy()
        swap = np.logical_not(np.sign((m6 - m5)[:, 0]) == self.dir)
        self.markers[swap, -4: -2] = m6[swap]  # NOTE: m5 > swap < m6.
        self.markers[swap, -2:] = m5[swap]
        logging.debug("%s - Reordenamiento de pie A1" % self)

    @property
    def imarkers(self):
        u"""Generador(index)de la subdivisión de marcadores."""
        i = COLITEMS[:1].sum()
        for mxr in self.nmxroi * 2:
            yield np.arange(i, i + mxr)
            i += mxr

    def interpolateMarkers(self):
        u"""Crea los centro de marcadores de los cuadros incompletos"""
        fs = self.fullschema
        rows = np.arange(self.array.shape[0])
        for r , imarkers in zip(range(2, NREGIONS + 2), self.imarkers):
            nfs = np.bool8(self.array[:, r])
            for c in imarkers:
                self.array[nfs, c] = np.interp(
                    rows[nfs], rows[fs], self.array[fs, c])
        logging.debug("%s - Marcadores interpoladas" % self)

    def process(self):
        self.calculateRegions()
        self.verify = config.getboolean("walk", "verify")
        if self.verify:
            self.verifyRegions()
        self.interpolateRegions()
        self.markersRecovery()
        self.sortingFoot1()
        self.interpolateMarkers()
        self.save()
        self.processed = True
        logging.info("%s - Procesada" % self)



class CycleArray(object):
    pass


class ParametersArray(object):
    pass
