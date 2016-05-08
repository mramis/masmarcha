#!usr/bin/env python
# coding: utf-8

'''DOCSTRING
'''

# Copyright (C) 2016  Mariano Ramis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# Paths

TYPOGRAPHYS = os.path.join(os.path.abspath('.'), 'tipografias')
IMAGES = os.path.join(os.path.abspath('.'), 'images')

# Constants

leftMargin = 2.3*cm
commonMargins = 2*cm

heightUnit = A4[1] / 30.0
widthUnit = A4[0] / 21.0

colors = {'grey'       : '#343435',
          'lightblue'  : '#76BBE0',
          'red'        : '#EA6123'}


