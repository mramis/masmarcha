#!usr/bin/env python
# coding: utf-8

'''DOCSTRING
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


import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from cycler import cycler


ticksMajorParams = {'which'      : 'major'  ,
                    'direction'  : 'inout' ,
                    'length'     : 13.     ,
                    'width'      : 2.      ,
                    'color'      : '0.5'   ,
                    'pad'        : 8.      ,
                    'top'        : 'off'   ,
                    'right'      : 'on'    ,
                    'labelright' : 'on'    ,
                    'labelsize'  : 'medium',
                    'labelcolor' : '0.5'   }

ticksMinorParams = {'which'      : 'minor'  ,
                    'direction'  : 'inout' ,
                    'length'     : 8.0     ,
                    'width'      : 2.      ,
                    'color'      : '0.5'   ,
                    'pad'        : 8.      ,
                    'top'        : 'off'   ,
                    'right'      : 'on'    }

textParams = {'color' : '0.2'      ,
              'name'  : 'monospace',
              'size'  : 'xx-large' ,
              'weight': 'light'    , 
              'style' : 'italic'   }

def personalizePlot(xLabel, yLabel, xlim=(-10, 10), ylim=(-10, 10)):
    ax = plt.gca()
    ax.set_xlabel(xLabel, **textParams)
    ax.set_ylabel(yLabel, **textParams)
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_color('0.5')
    ax.spines['bottom'].set_color('0.5')
    ax.spines['right'].set_color('0.5')
    ax.spines['left'].set_linewidth(3.0)
    ax.spines['bottom'].set_linewidth(3.0)
    ax.spines['right'].set_linewidth(3.0)
    ax.grid(True, which='both', axis='y')
    ax.grid(True, which='major', axis='x', color='0.5')
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))
    ax.tick_params(axis=u'both',**ticksMajorParams)
    ax.tick_params(axis=u'both',**ticksMinorParams)
    ax.set_prop_cycle(cycler(color=('0.2', '0.3', '0.4')))
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    ax.axhline(linewidth=0.75, color='k', linestyle='--')
    fig = ax.figure
    fig.tight_layout(pad=1.5)
    fig.set_figwidth(10, forward=True)
    fig.set_figheight(6, forward=True)
    fig.set_facecolor('white')
    return

