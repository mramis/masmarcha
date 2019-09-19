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
#!/usr/bin/env python3

from configparser import ConfigParser
from json import load

from engine import VideoEngine, KinoveaTrayectoriesEngine

from preview import path

if __name__ == '__main__':
    config = ConfigParser()
    config.read('/home/mariano/masmarcha/masmarcha.ini')

    schema = load(open(config.get('paths', 'schema')))

    print('Inicia Motor.')
    engine = VideoEngine(config, schema)
    engine.calibrate_camera("/home/mariano/masmarcha/capturas/damero.mp4", 'MOTOG3-Mariano')
