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

def dataToTime(data):
    if type(data) is not str:
        raise ValueError('data must be string')
    time = list(data)
    if ':' in time:
        h, m, s, cs = data.split(':')
        newTime = (
                float(h) / 3600 +
                float(m) / 60 +
                float(s) +
                float(cs) * 0.01
                )
        return newTime

def dataToFloat(data):
    if type(data) is not str:
        raise ValueError('data must be string')   
    noFloat = list(data)
    if ',' in noFloat:
        ent, dec = data.split(',')
        return float('{}.{}'.format(ent, dec))

def restructure(data):
    if type(data) is not str:
        raise ValueError('data must be string')
    value = list(data)
    returnValue = None
    if ':' in value:
        returnValue = dataToTime(data)
    elif ',' in value:
        returnValue = dataToFloat(data)
    elif '.' in value:
        returnValue = float(data)
    return returnValue

