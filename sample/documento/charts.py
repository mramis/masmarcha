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
import matplotlib.cm as colorMap
import matplotlib.ticker as ticker

import plotParams


def getPercentaje(array):
    reference = array.size
    newArray = np.ndarray(array.shape)
    for index, item in enumerate(array):
        newArray[index] = item * 100.0 / reference
    return newArray

def percentajeLabel(value, pos):
    return '{:0.1f}%'.format(value)

def timeJointPlot(jointAngles,XLimits, YLimits, keys='joint'):
    axes = plt.gca()
    axes.xaxis.set_major_formatter(ticker.FuncFormatter(percentajeLabel))
    time = getPercentaje(np.arange(jointAngles.size))
    plotParams.personalizePlot(
            u'Ciclo',
            u'-Extensión / +Flexión',
            xlim=XLimits,
            ylim=YLimits
            )
    plt.plot(time, jointAngles, linewidth=3.0, color='0.7')
    plt.savefig(keys)
    plt.close()

def jointJointPlot(jointX, jointY, XLimits, YLimits, keys='joints'):
    plotParams.personalizePlot(
            u'Angulos de {}'.format(keys[0]),
            u'Angulos de {}'.format(keys[-1]),
            xlim=XLimits,
            ylim=YLimits
            )
    colormap = colorMap.hsv(np.arange(jointX.size))
    startPatch = mpatches.Patch(color=colormap[0], label='Start')
    endPatch = mpatches.Patch(color=colormap[-1], label='End')
    plt.legend(handles=[startPatch, endPatch], frameon=False)
    for i, point in enumerate(jointX):
        plt.scatter(jointX[i], jointY[i], color=colormap[i])
    plt.savefig('{}-{}'.format(*keys))
    plt.close()

