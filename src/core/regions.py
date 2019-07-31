#!/usr/bin/env python3
# coding: utf-8

u"""El manejo de los datos de regiones."""

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
