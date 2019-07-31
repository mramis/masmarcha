#!/usr/bin/env python3
# coding: utf-8

u"""Interpolación de los valores faltantes en la eploración del video."""

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





class MarkersInterpolator(Interpolator):

    def interpolate(self):
        u"""Realiza la interpolación de los marcadores de cuadros incompletos."""
        arr = self.warray.primary
        x = np.arange(self.warray.size)
        fs = np.bool8(arr[:, self.warray.fullschema_col])
        cols = self.warray.coordinates_cols
        for interp_indicator in self.warray.interpolation_indicator_cols:
            nofs = np.bool8(arr[:, interp_indicator])
            fsi = np.logical_not(nofs)
            self.interpolation2D(arr, x[nofs], x[np.logical_or(fs, fsi)], cols)
