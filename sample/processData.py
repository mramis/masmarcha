#!/usr/bin/env python
# coding: utf-8

'''Docstring
'''

# Copyright (C) 2016  Mariano Ramis

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

import os

import numpy as np

from lectura.authorizedText import evaluated
from lectura.extractArrays import textToArray
from calculo.joints import hipAngles, kneeAngles, ankleAngles, Direction
from calculo.calculations import polynomialRegression
from calculo.interpolation import extendArraysDomain, interpolateArray
from plots.charts import timeJointPlot, jointJointPlot

def extractJointMarkersArraysFromFiles(files):
    '''Args:
        List of "Kinovea Software" output text files with joint markers.
    Returns:
        Dictionary where that keys are the filenames of files input
            and values are numpy arrays of that points.
    '''
    output = {}
    for file_path in files:
        abs_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path).split('.', 1)[0]
        if not evaluated(abs_path):
            message = ('El archivo {} no es correcto'.format(abs_path))
            raise Exception(message)
        array = textToArray(abs_path)
        output[filename] = array
    return output

def extractJointAnglesFromJointMarkersArrays(points_array):
    '''Args:
        Dictionary of joint-markers-array.
    Return:
        Dictionary of "filenames : {joint-angles-array}", where keys are
        filenames and values are dictionarys of joint-angles.
    '''
    angles_array = {}
    for filename, array in points_array.iteritems():
        joints = {}
        try:
            hip_p, knee_p, ankle_p, foot_p = array
            direction = Direction(array)
            joints['hip'] = hipAngles(hip_p, knee_p, direction)
            joints['knee'] = kneeAngles(hip_p, knee_p, ankle_p, direction)
            joints['ankle'] = ankleAngles(knee_p, ankle_p, foot_p)
            angles_array[filename] = joints
        except ValueError:
            message = "The marker-joint-arrays number does't correct"
            raise Exception(message)
    return angles_array

def plotJointAnglesArrays(angles_array):
    '''
    '''

    hip = [joint['hip'] for joint in angles_array.values()]
    knee = [joint['knee'] for joint in angles_array.values()]
    ankle = [joint['ankle'] for joint in angles_array.values()]

    if len(hip) > 1: # or knee or ankle, all must've the same length
        fixed_hip, hip_domain = extendArraysDomain(*hip)
        fixed_knee, knee_domain = extendArraysDomain(*knee)
        fixed_ankle, ankle_domain = extendArraysDomain(*ankle)

        # overwritten the originals variables
        hip = [interpolateArray(array, hip_domain) for array in fixed_hip]
        knee = [interpolateArray(array, knee_domain) for array in fixed_knee]
        ankle = [interpolateArray(array, ankle_domain) for array in fixed_ankle]

    for array in hip:# no está bien para cuando hip es un solo dato!!!
        y_sup_lim = int(max(array[1]))
        y_inf_lim = int(min(array[1]))
        y_limits = [-20, 50]
        if y_sup_lim > 50:
            y_limits[1] = y_sup_lim + 10
        if y_inf_lim < -20:
            y_limits[0] = y_inf_lim - 10
        timeJointPlot(array[1], array[0], YLimits=y_limits)


if __name__ == '__main__':
    import os
    kinovea_files = [
            ('./test/kinoveatext/TPlano.txt'),
            ('./test/kinoveatext/MPlano.txt')
    ]

    joint_markers_array = extractJointMarkersArraysFromFiles(kinovea_files)
    joint_angles_array = extractJointAnglesFromJointMarkersArrays(joint_markers_array)
    plotJointAnglesArrays(joint_angles_array)

