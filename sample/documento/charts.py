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

def timeJointPlot(jointAngles, polyFit, XLimits, YLimits, keys='joint'):
    axes = plt.gca()
    axes.xaxis.set_major_formatter(ticker.FuncFormatter(percentajeLabel))
    time = getPercentaje(np.arange(jointAngles.size))
    plotParams.personalizePlot(
            u'Ciclo',
            u'-Extensión / +Flexión',
            xlim=XLimits,
            ylim=YLimits
            )
    KinoveaData = plt.plot(
            time,
            jointAngles,
            linestyle='-',
            color='r',
            linewidth='0.5',
            marker='o',
            markeredgecolor='r',
            #markerfacecolor='none'
            )
    polynomialFit = plt.plot(
            time,
            polyFit[0],
            linewidth=3.5,
            color='0.6'
            )
    plt.legend(
            (u'DatosKinovea', u'RegeresiónPolinómica'),
            fontsize='x-small',
            numpoints=1,
            fancybox=True,
            framealpha=.5,
            borderaxespad=1,
            )
    plt.axhline(0, linestyle='--', linewidth=0.7, color='0.1')
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
    startPatch = mpatches.Patch(color=colormap[0], label='InicioCiclo')
    endPatch = mpatches.Patch(color=colormap[-1], label='FinalCiclo')
    plt.legend(
            handles=[startPatch, endPatch],
            fontsize='x-small',
            numpoints=1,
            fancybox=True,
            framealpha=.5,
            borderaxespad=1
            )
    for i, point in enumerate(jointX):
        plt.scatter(jointX[i], jointY[i], color=colormap[i])
    plt.axvline(0, linestyle='--', linewidth=0.7, color='0.1')
    plt.axhline(0, linestyle='--', linewidth=0.7, color='0.1')
    plt.savefig('{}-{}'.format(*keys))
    plt.close()

