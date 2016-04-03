#!usr/bin/env python
# coding: utf-8

'''Here's it's defined canonical R2 vertical axis vectors.
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


from numpy import zeros

def positiveY(RowDim):
    array = zeros((RowDim, 2))
    array.T[1] = 1
    return array

def negativeY(RowDim):
    array = zeros((RowDim, 2))
    array.T[1] = -1
    return array

def positiveX(RowDim):
    array = zeros((RowDim, 2))
    array.T[0] = 1
    return array

def negativeX(RowDim):
    array = zeros((RowDim, 2))
    array.T[0] = -1
    return array
