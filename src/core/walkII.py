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

import numpy as np

from .regions import Regions
from .markers import Markers


class WalkArray(object):
    u""" El arreglo que utiliza Caminata(Walk) para almacenar datos.

        Tiene dos estructuras de datos:

        1) El arreglo principal (2d numpy.array) tiene 3 secciones:
        - la primer sección de 4 columnas: datos boleanos de control.
            # 1er lugar para el boleano que indica esquema completo.
            # 2do-4to lugar para los boleanos de regiones incompletas.
        - la segunda sección Mx2 columas: datos de marcadores (#M) extraídos
          del cuadro de video.
            # 5to lugar para la posición del cuadro de video del cuál salen los
              marcadores.
            # 6to-m_ésimo lugar para los pares coordenados (x, y) de los
              marcadores.
        - la tercera sección Rx4 columnas: datos de regiones (#R) de interés
          (regiones de agrupamiento de marcadores).
            # m_ésimo-r_ésimo lugar para las esquinas (2 pares coordenados) de
              las regiones.

        2) El arreglo secundario es una lista (list) que contiene los datos de
        los cuadros de video de esquema incompleto (por falta o por exceso) y
        se utiliza para completar el arreglo principal.

    """
    def __init__(self, config, schema):
        self.config = config
        self.schema = schema
        self.sections = np.array((4, 1 + schema["n"]*2, schema["r"]*4))
        self.baseshape = (config.getint("walk", "maxsize"), sum(self.sections))
        self.primary = np.zeros(self.baseshape, dtype="int16")
        self._secondary = []

    @property
    def size(self):
        return self.primary.shape[0]

    @property
    def dir(self):
        u"""Alias de Walk.direction."""
        return self.direction

    @property
    def direction(self):
        """Devuelve la dirección de la caminata."""
        columns = tuple(self.x_coordinates_cols_by_roi)[0]
        pos_difference = self.primary[-1, columns] - self.primary[0, columns]
        return -1 if np.mean(pos_difference) < 0 else 1

    @property
    def fullschema_col(self):
        u"""El índice de columna boleana de esquema completo."""
        return 0

    @property
    def posframe_col(self):
        u"""El índice de columna de posición del cuadro dentro del video."""
        return self.sections[:1].sum()

    @property
    def coordinates_cols(self):
        u"""Range de columnas de las coordenadas (x, y) de los marcadores."""
        return range(self.posframe_col + 1, self.sections[:2].sum())

    @property
    def regions_cols(self):
        u"""Range de columnas de las coordenadas (x, y) de las regiones."""
        return range(self.sections[:2].sum(), self.sections[:3].sum())

    @property
    def num_of_markers_per_roi(self):
        u"""Número de marcadores por región de interés."""
        return np.intp(self.schema["markersxroi"])

    @property
    def x_coordinates_cols_by_roi(self):
        u"""Generador de Slices de la subdivisión "x" de marcadores por cada región."""
        start_index = self.posframe_col + 1
        ncoordinates = 2
        movement_per_roi = self.num_of_markers_per_roi * ncoordinates
        for mov in movement_per_roi:
            yield slice(start_index, start_index + mov, ncoordinates)
            start_index += mov

    @property
    def y_coordinates_cols_by_roi(self):
        u"""Generador de Slices de la subdivisión "y" de marcadores por cada región."""
        return (
            slice(s.start + 1, s.stop + 1, s.step)
            for s in self.x_coordinates_cols_by_roi
        )

    @property
    def m_coordinates_cols_by_roi(self):
        u"""Lista con las cordenadas de los marcadores por región de interés."""
        start_index = self.posframe_col + 1
        coordinates = []
        movement_per_roi = self.num_of_markers_per_roi * 2
        for mov in movement_per_roi:
            coordinates.append(slice(start_index, start_index + mov))
            start_index += mov
        return coordinates

    @property
    def corner_regions_points_cols(self):
        u"""Generador de Slices de esquinas (puntos) de regiones por región."""
        start = self.sections[:2].sum()
        ncoordinates = 4
        start_indexes = [
            start + (roi * ncoordinates)
            for roi in range(self.schema["r"])
        ]
        end_indexes = [
            start + ((roi + 1) * ncoordinates)
            for roi in range(self.schema["r"])
        ]
        return (
            slice(start, stop)
            for (start, stop) in zip(start_indexes, end_indexes)
        )

    @property
    def interpolation_indicator_cols(self):
        u"""Devuelve los índices de columna de marcadores a interpolar."""
        return (1, 2, 3)

    def resize(self):
        u"""Modifica por incremento el tamaño de filas del arreglo principal."""
        extension = np.zeros(self.baseshape, dtype="int16")
        self.primary = np.vstack((self.primary, extension))

    def save(self):
        return NotImplemented


# class ArrayRow(object):
#
#     def __init__(self, warray):
#         self.value = 0
#         self.size_observer = ArraySizeObserver(warray)
#
#     def __call__(self):
#         return self.value
#
#     def increment(self):
#         u"""Incrementa el valor de fila corriente."""
#         self.value += 1
#         self.size_observer.checkSize(self.value)
#
#
# class ArraySizeObserver(object):
#
#     def __init__(self, warray):
#         self.warray = warray
#         self.reference_size = None
#         self.uploadReferenceSize()
#
#     def checkSize(self, value):
#         u"""Supervisa el tamaño del arreglo principal de WalkArray."""
#         if value == self.reference_size - 1:
#             self.resizeArray()
#
#     def resizeArray(self):
#         u"""Cambia el tamaño (en filas) del arreglo principal WalkArray."""
#         self.warray.resize()
#         self.uploadReferenceSize()
#
#     def uploadReferenceSize(self):
#         u"""Actualiza el valor de tamaño de referencia."""
#         self.reference_size = self.warray.primary.shape[0]
#
#
# class ArrayClose(object):
#
#     def __init__(self, warray):
#         self.warray = warray
#
#     def close(self, last_row_index, elements_to_remove):
#         u"""Cierra las estructuras al último dato de esquema completo."""
#         self.closePrimary(last_row_index - elements_to_remove)
#         self.closeSecondary(elements_to_remove)
#
#     def closePrimary(self, last_valid_row_index):
#         u"""Cierra el arreglo primario.
#
#         Recorta las filas que están de más en el arreglo primario.
#         """
#         self.warray.primary = self.warray.primary[
#             slice(0, last_valid_row_index)
#         ]
#
#     def closeSecondary(self, elements_to_remove):
#         u"""Cierra el arreglo secundario.
#
#         Elimina los últimos datos que se agregaron NO-esquema completo.
#         """
#         for __ in range(elements_to_remove):
#             self.warray._secondary.pop()
#
#
# class ArrayFrameDataInserter(object):
#
#     def __init__(self, warray):
#         self.warray = warray
#         self.current_row = ArrayRow(warray)
#         self.elements_to_remove = 0
#         self.close_data_structure = ArrayClose(warray)
#
#     def insert(self, fullschema, posframe, coordinates):
#         u"""Agrega datos al arreglo WalkArray."""
#         coordinates = coordinates.flatten()
#         try:
#             self.primaryInsert(fullschema, posframe, coordinates)
#         except ValueError:
#             self.SecondaryInsert(coordinates)
#         finally:
#             self.incrementRow()
#
#     def primaryInsert(self, fullschema, posframe, coordinates):
#         u"""Agrega datos al arreglo principal de WalkArray."""
#         row = self.current_row()
#         self.warray.primary[row, self.warray.posframe_col] = posframe
#         self.warray.primary[row, self.warray.fullschema_col] = fullschema
#         self.warray.primary[row, self.warray.coordinates_cols] = coordinates
#         self.elements_to_remove = 0
#
#     def SecondaryInsert(self, coordinates):
#         u"""Agrega datos al arreglo secundario de WalkArray."""
#         row = self.current_row()
#         self.warray._secondary.append((row, coordinates))
#         self.elements_to_remove += 1
#
#     def incrementRow(self):
#         u"""Incrementa en el número de fila de insercción de datos."""
#         self.current_row.increment()
#
#     def stopInsert(self):
#         u"""Al finalizar con la insercción de datos se cierran los arreglos."""
#         self.close_data_structure.close(
#             self.current_row(), self.elements_to_remove
#         )
#


# class RegionsCalculator(object):
#
#     def __init__(self, warray):
#         self.warray = warray
#         self.roiwidth = warray.config.getint("walk", "roiwidth")
#         self.roiheight = warray.config.getint("walk", "roiheight")
#
#     def getMaximum(self, coord_columns, extrapx):
#         u"""Calcula el valor máximo de las columnas del arreglo primario."""
#         return np.max(self.warray.primary[:, coord_columns], axis=1) + extrapx
#
#     def getMinimum(self, coord_columns, extrapx):
#         u"""Calcula el valor mínimo de las columnas del arreglo primario."""
#         return np.min(self.warray.primary[:, coord_columns], axis=1) - extrapx
#
#     def setRegions(self, xmin, ymin, xmax, ymax, roi):
#         u"""Establece las cordenadas de las esquinas de la región en el arreglo primario."""
#         roi_row = np.vstack((xmin, ymin, xmax, ymax)).transpose()
#         self.warray.primary[:, roi] = roi_row
#
#     def calculate(self):
#         u"""Calcula ls esquinas (tp-lf, bt-rg) de las regiones de agrupamiento."""
#         walk_array_slice_columns = zip(
#             self.warray.x_coordinates_cols_by_roi,
#             self.warray.y_coordinates_cols_by_roi,
#             self.warray.corner_regions_points_cols
#         )
#         for x, y, roi in walk_array_slice_columns:
#             xmin = self.getMinimum(x, self.roiwidth)
#             xmax = self.getMaximum(x, self.roiwidth)
#             ymin = self.getMinimum(y, self.roiheight)
#             ymax = self.getMaximum(y, self.roiheight)
#             self.setRegions(xmin, ymin, xmax, ymax, roi)
#
#
# class Regions(object):
#
#     def __init__(self, warray):
#         self.warray = warray
#         self.calculator = RegionsCalculator(warray)
#         self.interpolator = RegionsInterpolator(warray)
#
#     def build(self):
#         u"""Construye las regiones de agrupamiento del esquema de marcadores."""
#         self.calculator.calculate()
#         self.interpolator.interpolate()
#


# class MarkersIdentifier(object):
#
#     def __init__(self, warray):
#         self.warray = warray
#         self._current_row = None
#
#     def markersInRegions(self, row, markers, roi):
#         u"""Devuelve los marcadores que se encuentran dentro de la región."""
#         rows = markers.size // 2
#         reshaped = markers.reshape((rows, 2))
#         roimin, roimax = self.warray.primary[row, roi].reshape((2, 2))
#         founded_markers = np.logical_and(roimin < reshaped, reshaped < roimax)
#         return reshaped[np.logical_and(*founded_markers.transpose())].flatten()
#
#     def sizeMatch(self, expected_markers_size, markers):
#         u"""Compara el tamaño del arreglo de marcadores con el num esperado."""
#         return markers.size == expected_markers_size * 2  # componentes
#
#     def destBySize(self, nmarkers, markers):
#         u"""Decide el destino de los marcadores encontrados en la región."""
#         if self.sizeMatch(nmarkers, markers):
#             self.toPrimaryArray(markers)
#         else:
#             self.toInterpolate()
#
#     def toInterpolate(self):
#         u"""Marcadores que tienen que ser interpolados."""
#         column = self.warray.interpolation_indicator_cols[self._current_roi]
#         self.warray.primary[self._current_row, column] = 1
#
#     def toPrimaryArray(self, markers,):
#         u"""Marcadores que se pudieron identificar."""
#         column = self.warray.interpolation_indicator_cols[self._current_roi]
#         self.warray.primary[self._current_row, column] = 0
#
#         columns = self.warray.m_coordinates_cols_by_roi[self._current_roi]
#         self.warray.primary[self._current_row, columns] = markers
#
#     def identify(self):
#         u"""Identifica los marcadores de cada región."""
#         for row, markers in self.warray._secondary:
#             self._current_row = row
#             iter_regions = zip(
#                 self.warray.num_of_markers_per_roi,
#                 self.warray.corner_regions_points_cols
#             )
#             for r, (nmarkers, roi) in enumerate(iter_regions):
#                 self._current_roi = r
#                 sub_roi_markers = self.markersInRegions(row, markers, roi)
#                 self.destBySize(nmarkers, sub_roi_markers)


# class MarkersFootSorter(object):
#
#     def __init__(self, warray):
#         self.warray = warray
#
#     @property
#     def foot(self):
#         columns = self.warray.m_coordinates_cols_by_roi[-1]
#         return self.warray.primary[:, columns]
#
#     @foot.setter
#     def foot(self, markers):
#         columns = self.warray.m_coordinates_cols_by_roi[-1]
#         self.warray.primary[:, columns] = markers
#
#     def footMaskDirection(self, m5, m6):
#         u"""Compara la dirección del pié con el de la caminata."""
#         return np.logical_not(
#             np.equal(
#                 np.sign((m6 - m5)[:, 0]),
#                 np.repeat(self.warray.direction, self.warray.size)
#             )
#         )
#
#     def swap(self, mask, first, second):
#         u"""Intercambia la posición de los marcadores según "mask"."""
#         temp = first.copy()
#         first[mask] = second[mask]
#         second[mask] = temp[mask]
#         return (first, second)
#
#     def splitFoot(self):
#         u"""Divide el grupo de pie en los marcadores correspondientes."""
#         return self.foot[:, -4: -2], self.foot[:, -2:]
#
#     def joinFoot(self, m5, m6):
#         u"""Ensambla los marcadores de pié ya ordenados en el arreglo principal."""
#         m4 = self.foot[:, -6: -4]
#         self.foot = np.block([m4, m5, m6])
#
#     def sort(self):
#         u"""Ordena los marcadores del pie."""
#         m5, m6 = self.splitFoot()
#         mask = self.footMaskDirection(m5, m6)
#         m5, m6 = self.swap(mask, m5, m6)
#         self.joinFoot(m5, m6)


# class Markers(object):
#
#     def __init__(self, warray):
#         self.warray = warray
#         self.identifier = MarkersIdentifier(warray)
#         self.sorter = MarkersFootSorter(warray)
#         self.interpolator = MarkersInterpolator(warray)
#
#     def fix(self):
#         self.identifier.identify()
#         self.sorter.sort()
#         self.interpolator.interpolate()


class Walk(object):
    __count = 0

    def __init__(self, config, schema):
        Walk.__count += 1
        self.id = Walk.__count
        self.warray = WalkArray(config, schema)
        self.inserter = ArrayFrameDataInserter(self.warray)
        self.regions = Regions(self.warray)
        self.markers = Markers(self.warray)
        self.processed_flag = False

    def __repr__(self):
        return "{!s}-ID{!s}".format(self.__class__.__name__, self.id)

    @classmethod
    def num_of_walks(cls):
        return cls.__count

    @classmethod
    def restart(cls):
        cls.__count = 0

    @property
    def duration(self):
        return self.warray.size

    @property
    def startframe(self):
        return int(self.warray.primary[0, self.warray.posframe_col])

    @property
    def endframe(self):
        return int(self.warray.primary[-1, self.warray.posframe_col])

    @property
    def markersView(self):
        u"""."""
        return self.warray.primary[:, self.warray.coordinates_cols]

    @property
    def regionsView(self):
        u"""."""
        return self.warray.primary[:, self.warray.regions_cols]

    @property
    def interpolation_indicators(self):
        u"""."""
        return self.warray.primary[:, self.warray.interpolation_indicator_cols]

    def getStartPos(self, posframe):
        u"""Devuelve la posición de inicio de caminata."""
        return np.where(
            self.warray.primary[:, self.warray.posframe_col] == posframe)[0]

    def insert(self, fullschema, posframe, coordinates):
        u"""Agrega datos al arreglo."""
        self.inserter.insert(fullschema, posframe, coordinates)

    def stop(self):
        """Cierra el arreglo con los últimos datos de esquema completo."""
        self.inserter.stopInsert()

    def process(self):
        u"""."""
        self.regions.build()
        self.markers.fix()
        self.processed_flag = True
