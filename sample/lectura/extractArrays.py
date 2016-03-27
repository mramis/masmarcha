#!usr/bin/env python
# coding: utf-8

'''Read and extract data in array form from text file.
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

from numpy import array as NParray
from fixData import restructure

def textToArray(textfile, separator='0:00:00:00'):

    with open(textfile) as f:
        _file = f.read()

# split the text data by zero time
    textArrayss = _file.split(separator)
    textArrayss.pop(0) # the Kinovea introduction

# split each line(row) from each array to lines components
    linesArrays = []
    for array in textArrayss:
        linesArrays.append(array.split('\n'))

# remove all empty data and keep with time, x & y components
    arrays = []
    for array in linesArrays:
        array.pop(0) # the first (x=0, y=0) components
        newArray = []
        for line in array:
            cell = line.split()
            if cell:
                newCell = []
                for item in cell:
                    newCell.append(restructure(item))
                newArray.append(newCell)
        arrays.append(newArray)
    return NParray(arrays, dtype=float)


