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

import numpy as np
import matplotlib.pyplot as plt

import plotParams
import cyclePercent

class AnglePlot(object):

    def __init__(self, filename):
        self._filename = filename

    def configure(self, ylimits=None):
        plotParams.personalizePlot(
                u'Ciclo', u'-Extensión / +Flexión',
                xlim=(0, 100), ylim=ylimits
        )

    def buildTimeAnglePlot(self, Angles, X=None, poly_fit=False):
        
        
        if isinstance(X, np.ndarray):
            time = cyclePercent.getPercentaje(X)
        else:
            time = cyclePercent.getPercentaje(np.arange(Angles.size))

        plt.plot(
                time, Angles, linestyle='-', color='r',
                linewidth='.5', marker='o', markeredgecolor='r'
        )
        plt.axhline(0, linestyle='--', linewidth=.7, color='0.1')
        legend_labels = u'DatosKinovea'

        plt.legend(
                legend_labels, fontsize='x-small', numpoints=1,
                fancybox=True, framealpha=.5, borderaxespad=1
        )

    def showPLot(self):
        plt.show()

    def savePlot(self):
        plt.savefig('{}.png'.format(self._filename))
        plt.close()


miplot = AnglePlot('test.png')
miplot.configure(ylimits=(-20, 100))
miplot.buildTimeAnglePlot(np.power(np.arange(10), 2))
miplot.buildTimeAnglePlot(np.power(np.arange(10), 3))
miplot.showPLot()



