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
from documento.charts import timeJointPlot, jointJointPlot

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

def operateOverJointMarkersArrays(points_array):
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

def operateOverJointAnglesArrays(angles_array):
    
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

    ####
    import matplotlib.pyplot as plt
    for data in hip:
        plt.plot(data.T[0], data.T[1])
    plt.show()

    for data in knee:
        plt.plot(data.T[0], data.T[1])
    plt.show()

    for data in ankle:
        plt.plot(data.T[0], data.T[1])
    plt.show()


if __name__ == '__main__':
    import os
    kinovea_files = [
            os.path.abspath('../test/kinoveatext/TPlano.txt'),
            os.path.abspath('../test/kinoveatext/MPlano.txt')
    ]

    joint_markers_array = extractJointMarkersArraysFromFiles(kinovea_files)
    joint_angles_array = operateOverJointMarkersArrays(joint_markers_array)

    operateOverJointAnglesArrays(joint_angles_array)

