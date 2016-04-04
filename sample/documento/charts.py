#!usr/bin/env python
# coding: utf-8

'''Generates data plots.
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
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import plotParams


def timeJointPlot(jointAngles, key='joint'):
    time = np.arange(jointAngles.size)
    plotParams.personalizePlot(
            u'% Ciclo(tiempo)',
            u'Angulos(extensión-flexión)',
            (-20, 70)
            )
    plt.plot(time, jointAngles, linewidth=3.0, color='0.7')
    plt.show()
    plt.close()

def jointJointPlot(jointX, jointY, key='joints'):
    axes = plt.gca()
    axes.set_aspect('equal', adjustable='box')
    plotParams.personalizePlot(
            u'Angulos {}'.format(key[0]),
            u'Angulos {}'.format(key[-1]),
            (-5, 5))
    colorMap = plt.cm.Greys(np.arange(jointX.size))
    startPatch = mpatches.Patch(
            edgecolor = '.5',
            facecolor=str(colorMap[0,0]),
            label='Start'
            )
    endPatch = mpatches.Patch(color=str(colorMap[-1,0]), label='End')
    plt.legend(handles=[startPatch, endPatch], frameon=False)
    plt.scatter(jointX, jointY, c=colorMap, edgecolor='0.5')
    plt.show()
    plt.close()

if __name__ == '__main__':
    X = np.linspace(-np.pi, np.pi, 100)
    Y = np.sqrt(10 - np.square(X)) 
    _Y = -np.sqrt(10 - np.square(X))

    jointJointPlot(np.append(X, -X), np.append(Y, _Y))
