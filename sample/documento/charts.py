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

def jointJointPLot(jointX, jointY, key='joints'):
    plt.scatter(jointX, jointY)
    plt.show()
    plt.close()

if __name__ == '__main__':
    X = np.linspace(-5, 5, 100)
    Y = np.exp2(X, np.ndarray(X.shape))

    timeJointPlot(Y)
