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
from calculo.statistics import cycleEqualizer, interpolateArray
from documento.charts import timeJointPlot, jointJointPlot

def processTextFiles(files):
    output = {}
    for _file in files:
        filename = os.path.basename(_file).split('.')[0]
        if not evaluated(_file):
            messa = ('El archivo {} no es correcto'.format(_file))
            raise Exception(messa)
        array = textToArray(_file)
        output[filename] = array
    return output

def operateOverArrays(arrays, destPath='.'):
    hip_joints = []
    knee_joints = []
    ankle_joints = []
    filenames = []
    for filename, array in arrays.iteritems():
        try:
            hip_p, knee_p, ankle_p, foot_p = array
        except:
            raise Exception("The number of joint-arrays does't correct")
        direction = Direction(array)
        hip = hipAngles(hip_p, knee_p, direction)
        knee = kneeAngles(hip_p, knee_p, ankle_p, direction)
        ankle =  ankleAngles(knee_p, ankle_p, foot_p)
        hip_joints.append(hip)
        knee_joints.append(knee)
        ankle_joints.append(ankle)
        filenames.append(filename)
    
    try:
        eq_hip_joints, domain = cycleEqualizer(np.array(hip_joints))
        for hip_array in eq_hip_joints:
            hip = interpolateArray(hip_array, domain)
            timeJointPlot(hip, polynomialRegression(hip, 10), -20, 50)
    except:
        print(hip)
        timeJointPlot(hip, polynomialRegression(hip, 10), -20, 50)
        


if __name__ == '__main__':
    import os
    _files = [os.path.abspath('./lectura/kinoveatext/TPlano.txt'),
              ]#os.path.abspath('./lectura/kinoveatext/MPlano.txt')]

    arrays = processTextFiles(_files)
    angles = operateOverArrays(arrays)

