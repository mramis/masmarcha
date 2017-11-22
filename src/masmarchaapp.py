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
            "capture": {
                "schema_path": None,
                "schema_indicator": '',
                "ft_mov_markers": None,
            },
            "paths": PATHS,
            "process": {
                "fourierfit": True,
                "f_coeff": 4,
            }
        }
        for section in default_config:
            config.add_section(section)
            config.setall(section, default_config[section])
        config.write()



if __name__ == '__main__':
    MasMarchaApp().run()
