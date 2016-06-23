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


def separator(textfile):
    '''this is with de assumption that file header it's lenght 2'''
    _file = open(textfile)
    for i, line in enumerate(_file):
        if i == 2:
            separator = line.split()[0]
            break
    _file.close()
    if separator != '0:00:00:00':
        raise Exception("the time format is not correct")
    return separator

def textToArray(textfile):
    sep = separator(textfile)
    with open(textfile) as f:
        _file = f.read()
#split the text data by zero time
    textArrayss = _file.split(sep)
    textArrayss.pop(0) # the Kinovea introduction
# split each line(row) from each array to lines components
    linesArrays = [array.split('\n') for array in textArrayss]
# remove all empty data and keep with time, x & y components
    arrays = []
    for array in linesArrays:
        x, y = array[0].split()
        if x == 0 and y == 0:
            raise Exception('Error with origin axis edited on kinovea')
        newArray = []
        for i, line in enumerate(array):
            cell = line.split()
            if cell:
                if i == 0:
                    cell.insert(0, sep)
                newCell = []
                for item in cell:
                    newCell.append(restructure(item))
                newArray.append(newCell)
        arrays.append(newArray)
    return NParray(arrays, dtype=float)
