#!/usr/bin/env python3
# coding: utf-8

u"""El manejo de los datos de marcadores."""

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
