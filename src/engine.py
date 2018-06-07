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

import logging
from collections import deque
import json

from .video import find_walks, markers_from_walks


class WalkExplorer(object):

    def __init__(self, filename, config):

        self.fnm = filename
        self.sch = json.load(open(config.get('engine', 'schema')))
        self.cym = config.get('engine', 'cycle_markers')
        self.pht = config.getfloat('engine', 'phase_threshold')
        self.rep = config.getfloat('engine', 'region_extrapx')
        self.mts = config.getfloat('engine', 'meter_scale')

    def run(self, bounds):
        markers_from_walks(self.fnm, bounds, self.sch, self.rep)
        logging.info('Fin de caminata {} [{}]'.format(self.fnm, bounds))

class VideoExplorer(object):

    def __init__(self, filename, config):
        self.config = config
        self.filename = filename

    def run(self):
        logging.info('Explorando: {}'.format(self.filename))
        walkexplorer = WalkExplorer(self.filename, self.config)
        for walkbounds in find_walks(self.filename, self.config):
            print(walkbounds)
            walkexplorer.run(walkbounds)
