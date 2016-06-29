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

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def addFonts(font_path):
    fonts = []
    toAdd = ('DIN-lightItalic.ttf'  ,
             'DINPro-light.ttf'     ,
             'DINPro-Regular.ttf'   ,
             'DINPro-Medium.ttf'    ,
             'GandhiSans-Bold.ttf'  ,
             'Letter-Gothic-Std.ttf')
    for font in toAdd:
            name = font.split('.')[0]
            path = os.path.join(font_path, font)
            pdfmetrics.registerFont(TTFont(name, path))
            fonts.append(name)
    return fonts

