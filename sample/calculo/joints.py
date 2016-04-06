#!usr/bin/env python
# coding: utf-8

'''Here's where it's definied joints angles.
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


import numpy as np

from canonicalVectors import positiveX, negativeX
from calculations import Angle, Direction

def hipAngles(hipArray, kneeArray, direction):
    HAP = hipArray[:, 1:] # without time
    KAP = kneeArray[:, 1:] # same here
    if type(HAP) is  np.ndarray and type(KAP) is  np.ndarray:
        thigh = KAP - HAP
        if direction is 1:
            hipAngle = 90 - Angle(thigh, positiveX(thigh.shape[0]))
        else:
            hipAngle = 90 - Angle(thigh, negativeX(thigh.shape[0]))
    else:
        raise Exception('hipArray&kneeArray must be numpy arrays')
    return  hipAngle

def kneeAngles(hipArray, kneeArray, ankleArray, direction):
    KAP = kneeArray[:, 1:]
    AAP = ankleArray[:, 1:] 
    TruthValueAnkle = type(AAP) is np.ndarray
    TruthValueKnee = type(KAP) is np.ndarray
    if TruthValueKnee and TruthValueAnkle:
        leg = AAP - KAP
        hipAngle = hipAngles(hipArray, kneeArray, direction)
        if direction is 1:
            lowKneeAngle = Angle(leg, positiveX(leg.shape[0])) - 90
        else:
            lowKneeAngle = Angle(leg, negativeX(leg.shape[0])) - 90
        kneeAngle = lowKneeAngle + hipAngle
    else:
        raise Exception('kneeArray&ankleArray must be numpy arrays')
    return kneeAngle

def ankleAngles(kneeArray, ankleArray, mttArray):
    KAP = kneeArray[:, 1:]
    AAP = ankleArray[:, 1:]
    MAP = mttArray[:, 1:]
    TruthValueKnee = type(KAP) is np.ndarray
    TruthValueAnkle = type(AAP) is np.ndarray
    TruthValueMtt = type(MAP) is np.ndarray
    if TruthValueKnee and (TruthValueAnkle and TruthValueMtt):
        leg = KAP - AAP
        foot = MAP - AAP
        ankleAngle = 90 - Angle(leg, foot)
    else:
        raise Exception('kneeArray&ankleArray&mttArray must be numpy arrays')
    return ankleAngle

