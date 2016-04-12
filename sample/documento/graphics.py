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


def chartBackground(pdfObject, x, y, width, height, title):
    pdfObject.setFillColor('#DCDCDD')
    pdfObject.roundRect(x,
                        y + height - 65,
                        width=width*0.5,
                        height=height*0.23,
                        radius=20,
                        stroke=0,
                        fill=1)

    pdfObject.setFillColor('#F5F5F5')
    pdfObject.roundRect(x,
                        y,
                        width=width,
                        height=height,
                        radius=10,
                        stroke=0,
                        fill=1)

