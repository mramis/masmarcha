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

from .array import WalkArray


class RegionsCalculator(object):

    def __init__(self, warray, configparser):
        self.warray = warray
        self.fields = warray.fieldsparser
        self.roiwidth = configparser.getint("walk", "roiwidth")
        self.roiheight = configparser.getint("walk", "roiheight")

    def getMaximum(self, coord_columns, extrapx):
        u"""Calcula el valor máximo de las columnas del arreglo primario."""
        return np.max(self.warray.array[:, coord_columns], axis=1) + extrapx

    def getMinimum(self, coord_columns, extrapx):
        u"""Calcula el valor mínimo de las columnas del arreglo primario."""
        return np.min(self.warray.array[:, coord_columns], axis=1) - extrapx

    def setRegions(self, xmin, ymin, xmax, ymax, roi):
        u"""Establece las cordenadas de las regiones en el arreglo primario."""
        roi_row = np.vstack((xmin, ymin, xmax, ymax)).transpose()
        self.warray.array[:, roi] = roi_row

    def getMarkersByRegion(self, coordinates="all"):
        u"""Devuelve un generador de campos (slice) de la posición de columnas
            de marcadores por cada región.
        """
        field_section = "markers region{r} {c}"
        return (
        self.fields.get(field_section.format(r=region, c=coordinates).split())
        for region in self.fields.regions
        )

    def getCornerPointsRegion(self, points="all"):
        u"""Devuelve un generador de campos (slice) de la posición de columnas
            de regiones por cada región.
        """
        field_section = "regions region{r} {p}"
        return (
        self.fields.get(field_section.format(r=region, p=points).split())
        for region in self.fields.regions
        )

    def calculate(self):
        u"""Calcula ls esquinas (tp-lf, bt-rg) de las regiones de
        agrupamiento.
        """
        x_markers_by_region = self.getMarkersByRegion("x")
        y_markers_by_region = self.getMarkersByRegion("y")
        region_corner_points_by_region = self.getCornerPointsRegion()

        walk_array_slice_columns = zip(
            x_markers_by_region,
            y_markers_by_region,
            region_corner_points_by_region,
        )

        for x, y, roi in walk_array_slice_columns:
            xmin = self.getMinimum(x, self.roiwidth)
            xmax = self.getMaximum(x, self.roiwidth)
            ymin = self.getMinimum(y, self.roiheight)
            ymax = self.getMaximum(y, self.roiheight)
            self.setRegions(xmin, ymin, xmax, ymax, roi)


class RegionsSupervisor(object):

    def __init__(self, warray, configparser):
        self.warray = warray
        self.fields = self.warray.fieldsparser
        self.centererror = configparser.getfloat("walk", "centererror")
        self.surfaceerror = configparser.getfloat("walk", "surfaceerror")

    # NOTE: DUPLICADO ver de pasar a fieldsparser
    def getCornerPointsRegion(self, points="all"):
        u"""Devuelve un generador de campos (slice) de la posición de columnas
            de regiones por cada región.
        """
        field_section = "regions region{r} {p}"
        return (
        self.fields.get(field_section.format(r=region, p=points).split())
        for region in self.fields.regions
        )

    @staticmethod
    def calculateSurfaceError(p0, p1):
        u"""Calcula el error cuadrático medio de área."""
        width, height = np.abs(p1 - p0).transpose()
        surface = width * height
        return np.abs(np.mean(surface) - surface)

    @staticmethod
    def calculateCenterError(p0, p1):
        u"""Calcula el error cuadrático medio del centro en y."""
        __, y_center = (p1 - p0).transpose() / 2
        y_center_mean = np.mean(y_center)
        return np.sqrt(np.power(y_center_mean - y_center, 2))

    @staticmethod
    def calculateErrorTolerance(error, tolerance):
        u"""Devuelve un vector boleano de valores que no pasan la tolerancia."""
        return error > max(error) * tolerance

    def setIndicator(self, roi, surface_error, center_error):
        u"""Establece valor de verdad True en las columnas de indicador de
        regiones que no pasan la prueba de tolerancia de valor de área y centro
        de trayectoria."""
        center_indicator = self.calculateErrorTolerance(
            center_error, self.surfaceerror
        )
        surface_indicator = self.calculateErrorTolerance(
            surface_error, self.surfaceerror
        )
        rows = np.logical_and(surface_indicator, center_indicator)
        region = ("region0", "region1", "region2")[roi]
        indicator_column = self.fields.get(["indicators", region])
        self.warray.array[rows, indicator_column] = 1

    def supervise(self):
        u"""Supervisa la trayectoria y el área de las regiones de interés."""
        points =  zip(
            self.getCornerPointsRegion('p0'),
            self.getCornerPointsRegion('p1')
        )
        for roi, (sp0, sp1) in enumerate(points):
            P0 = self.warray.array[:, sp0]
            P1 = self.warray.array[:, sp1]
            surface_error = self.calculateSurfaceError(P0, P1)
            center_error = self.calculateCenterError(P0, P1)
            self.setIndicator(roi, surface_error, center_error)


class RegionsInterpolator(object):

    def __init__(self, warray):
        self.warray = warray
        self.fields = self.warray.fieldsparser

    @staticmethod
    def interpolation2D(arr, xinterp, xvalues, ycolumns):
        u"""Genera los valores de interpolación."""
        for c in ycolumns:
            arr[xinterp, c] = np.interp(xinterp, xvalues, arr[xvalues, c])

    def interpolate(self):
        u"""Realiza la interpolación de las regiones de cuadros incompletos en
        el arreglo (in-place).
        """
        x = np.arange(self.warray.nrows)
        fs = np.bool8(self.warray.getView(["indicators", "initial"]))
        nofs = np.logical_not(fs)
        cols = self.fields.sliceToRange(self.fields.get(["regions", "all"]))
        self.interpolation2D(self.warray.array, x[nofs], x[fs], cols)


class Regions(object):

    def __init__(self, warray, configparser):
        self.calculator = RegionsCalculator(warray, configparser)
        self.supervisor = RegionsSupervisor(warray, configparser)
        self.interpolator = RegionsInterpolator(warray)

    def build(self):
        u"""Construye las regiones de agrupamiento del esquema de
        marcadores.
        """
        self.calculator.calculate()
        self.supervisor.supervise()
        self.interpolator.interpolate()


class MarkersIdentifier(object):

    def __init__(self, warray):
        self.warray = warray
        self.fields = warray.fieldsparser

    def getBreakArrayRows(self):
        u"""Las filas del arreglo que son de esquema incumplido inicialmente."""
        col = self.fields.get(['indicators', 'initial'])
        mask = np.bool8(self.warray.array[:, col])
        return np.arange(self.warray.nrows)[~mask]

    def reshapeMarkers(self, markers):
        u"""Cambia la forma de los marcadores 2D -> 3D."""
        nmarkers = self.fields.num_of_breakmarkers_columns // 2
        nrows, __ = markers.shape
        return np.reshape(markers, (nrows, nmarkers, 2))

    def getBreakMarkers(self, break_rows):
        u"""Los marcadores de esquema incumplido durante la exploración."""
        break_cols = self.fields.get(['breakmarkers', 'all'])
        break_markers = self.warray.array[break_rows, break_cols]
        return self.reshapeMarkers(break_markers)

    def reshapeRegion(self, region_points):
        u"""Cambia la forma de las regiones 2D -> 3D."""
        nrows = region_points.shape[0]
        nmarkers = self.fields.num_of_breakmarkers_columns // 2
        repeated = np.repeat(region_points, nmarkers, axis=0)
        return repeated.reshape(nrows, nmarkers, 2)

    def getBreakRegions(self, region, break_rows):
        u"""Generador. Arreglo de puntos esquina por región."""
        field = "regions region{r} {p}"
        p0_break_cols = self.fields.get(field.format(r=region, p="p0").split())
        p1_break_cols = self.fields.get(field.format(r=region, p="p1").split())
        return (
            self.reshapeRegion(self.warray.array[break_rows, p0_break_cols]),
            self.reshapeRegion(self.warray.array[break_rows, p1_break_cols])
        )

    def getExpectedsCountOfMarkersByRegion(self, region):
        u"""El número esperado de marcadores por según la región."""
        return self.fields.num_of_markers_per_region[region]

    def getDestinationArrayColumnsByRegion(self, region):
        u"""Las columnas de los marcadores hallados en la región."""
        field = "markers region{r} all"
        return self.fields.get(field.format(r=region).split())

    def getMaskMarkersInsideRegionPoints(self, markers, p0, p1):
        u"""Devuelve los marcadores que se encuentran dentro de la región."""
        founded_markers = np.logical_and(p0 < markers, markers < p1)
        mask = np.logical_and(*founded_markers.transpose()).transpose()
        selector = np.repeat(mask, 2, axis=1)
        return selector.reshape(markers.shape)

    def getInsideCountMatch(self, region, inside_mask):
        u"""Compara el tamaño del arreglo de marcadores con el num esperado."""
        matched_count = np.sum(np.count_nonzero(inside_mask, axis=2), axis=1)
        expected_size = self.getExpectedsCountOfMarkersByRegion(region)
        return np.equal(matched_count, expected_size * 2)

    def setRegionIndicator(self, region, rows_index):
        u"""Establece el valor de región completa en la columna de indicadores."""
        indicator = "indicators region{}".format(region).split()
        col = self.fields.get(indicator)
        self.warray.array[rows_index, col] = 1

    def allocate(self, region, rows, markers):
        u"""Coloca los marcadores encontrados en las columnas correspondientes."""
        dest_cols_by_region = self.getDestinationArrayColumnsByRegion(region)
        dest_shape = self.warray.array[rows, dest_cols_by_region].shape
        reshaped =  markers.reshape(dest_shape)
        self.warray.array[rows, dest_cols_by_region] = reshaped

    def identifyByRegion(self, region, rows, markers):
        u"""Identifica los marcadores que pertenecen a la región."""
        p0, p1 = self.getBreakRegions(region, rows)
        inside_mask = self.getMaskMarkersInsideRegionPoints(markers, p0, p1)
        markers_count_mask = self.getInsideCountMatch(region, inside_mask)
        inside_mask[~markers_count_mask] = False
        self.setRegionIndicator(region, rows[markers_count_mask])
        self.allocate(region, rows[markers_count_mask], markers[inside_mask])

    def identify(self):
        u"""Realiza la identificación de marcadores de esquema incumplido."""
        rows = self.getBreakArrayRows()
        markers = self.getBreakMarkers(rows)
        for r in self.fields.regions:
            self.identifyByRegion(r, rows, markers)


class MarkersFootSorter(object):

    def __init__(self, warray):
        self.warray = warray
        self.fields = warray.fieldsparser

    def getFoot(self):
        u"""Las coordenadas de los marcadores de pie."""
        m5_slice = self.fields.get(["markers", "region2", "m5"])
        m6_slice = self.fields.get(["markers", "region2", "m6"])
        return (
            self.warray.array[:, m5_slice],
            self.warray.array[:, m6_slice]
        )

    def footMaskDirection(self, m5, m6):
        u"""Compara la dirección del pié con el de la caminata."""
        return np.logical_not(
            np.equal(
                np.sign((m6 - m5)[:, 0]),
                np.repeat(self.warray.direction, self.warray.nrows)
            )
        )

    def swapMarkers(self, mask, first, second):
        u"""Intercambia la posición de los marcadores según "mask"."""
        temp = first.copy()
        first[mask] = second[mask]
        second[mask] = temp[mask]
        return (first, second)

    def setFoot(self, m5, m6):
        u"""Establece los valores corregidos de los marcadores."""
        m5_slice = self.fields.get(["markers", "region2", "m5"])
        m6_slice = self.fields.get(["markers", "region2", "m6"])
        self.warray.array[:, m5_slice] = m5
        self.warray.array[:, m6_slice] = m6

    def sort(self):
        u"""Ordena los marcadores del pie."""
        m5, m6 = self.getFoot()
        mask = self.footMaskDirection(m5, m6)
        swapped_m5, swapped_m6 = self.swapMarkers(mask, m5, m6)
        self.setFoot(swapped_m5, swapped_m6)


class MarkersInterpolator(object):

    def __init__(self, warray):
        self.warray = warray
        self.fields = warray.fieldsparser

    @staticmethod
    def interpolation2D(arr, xinterp, xvalues, ycolumns):
        u"""Genera los valores de interpolación."""
        for c in ycolumns:
            arr[xinterp, c] = np.interp(xinterp, xvalues, arr[xvalues, c])

    def interpolateByRegion(self, r, x, initial_indicators):
        u"""."""
        r = "region{}".format(r)
        region_indicators = self.warray.getView(["indicators", r])

        fs = np.logical_or(initial_indicators, region_indicators)
        nofs = np.logical_not(fs)
        field = self.fields.get(["markers", r, "all"])
        columns = self.fields.sliceToRange(field)
        self.interpolation2D(self.warray.array, x[nofs], x[fs], columns)

    def interpolate(self):
        u"""Realiza la interpolación de las regiones de cuadros incompletos en
        el arreglo (in-place).
        """
        x = np.arange(self.warray.nrows)
        initial_indicator = self.warray.getView(["indicators", "initial"])
        for r in self.fields.regions:
            self.interpolateByRegion(r, x, initial_indicator)


class Markers(object):

    def __init__(self, warray):
        self.warray = warray
        self.identifier = MarkersIdentifier(warray)
        self.sorter = MarkersFootSorter(warray)
        self.interpolator = MarkersInterpolator(warray)

    def fix(self):
        self.identifier.identify()
        self.sorter.sort()
        self.interpolator.interpolate()


class Walk(object):
    __counter = 0

    def __init__(self, config):
        Walk.__counter += 1
        self.id = Walk.__counter
        self.warray = WalkArray()
        self.markers = Markers(self.warray)
        self.regions = Regions(self.warray, config)

    def __str__(self):
        return "Caminata {}".format(self.id)

    @classmethod
    def num_of_walks(cls):
        return cls.__counter

    @classmethod
    def restart(cls):
        cls.__counter = 0

    def insert(self, pos, full, framedata):
        self.warray.addFrameData((pos, full, framedata))

    def stop(self):
        self.warray.close()

    def process(self):
        u"""."""
        self.regions.build()
        self.markers.fix()
