#!/usr/bin/env python
# coding: utf-8
"""En construcción."""

# Copyright (C) 2017  Mariano Ramis

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

from kivy.app import App

from uix.files import Content
from basicconfig import PATHS


class MasMarchaApp(App):
    u"""."""

    def build(self):
        u"""."""
        return Content()

    def build_config(self, config):
        u"""."""
        default_config = {
            "input-widget": {
                "schema-indicator": ''
            },
            "paths": PATHS,
            "engine": {
                "mode": "debug",
                "image_threshold": 240.0,
                "ratio_scale": 1.0,
                "ph_threshold": 2.5,
                "cy_markers": "M5-M6",
                "fft_scope": 4,
                "ffit": True,
            }
        }
        for section in default_config:
            config.add_section(section)
            config.setall(section, default_config[section])
        config.write()


"""
hardcore to setting:
dilatacion: valor entero para dilatar los marcadores.
thres: umbral de blancos.
roi_amp: la aplitud para la buqueda de región de interés en rodilla.
nomarkerstime: el tiempo que se utiliza para separar la caminta de otra
distinta.
dref: la cantidad de marcadores de referencia para pasar de pixeles a metros.
cal_frames: cantidad de cuadros en los que se espera encontrar los marcadores
para la calibración de la imagen.
cycle_level: es el umbral para determinar la velocidad de marcadores.
stance_swing_markers: decide si se utiliza el patrón definido por esquema para
la medición de velocidad de pie, o puede alterarse.
homogenize: limite de ciclos máximo por caminata.
fuirier_amp: si se aplica el filtrado de furier entonces se deben especificar
la cantidad de coeficientes.
"""


if __name__ == '__main__':
    MasMarchaApp().run()
