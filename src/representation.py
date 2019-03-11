#!/usr/bin/env python3
# coding: utf-8

"""Visualización de parámetros de marcha humana (cinemática).

Representaciones es el módulo que se encarga de la construcción de las gráficas
y tablas. Los dos tipos básicos son ángulos y parámetros espaciotemporales.
Los gráficos de los ángulos articulares pueden ser individuales o compartir
archivo de dibujo. Los parámetros espacio temporales se ubican en tablas con
formato de archivo de dibujo.
"""

# Copyright (C) 2017  Mariano Ramis

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
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


class Curves(object):

    def __init__(self, config):
        self.subplotparams = {'top':.85, 'wspace':.5}
        self.config = config
        self.figure = None
        self._color = None
        self.title = ""
        self.ndata = 0
        self.axes = []

    @property
    def color(self):
        if self._color:
            return self._color
        return plt.cm.Spectral(np.linspace(0, 1, self.ndata))

    @color.setter
    def color(self, value):
        self._color = value

    def new_figure(self, title):
        dpi = self.config.getint('plots', 'dpi')
        width = self.config.getint('plots', 'chartwidth')
        height = self.config.getint('plots', 'chartheight')
        fontsize = self.config.getint('plots', 'titlesize')
        self.figure = plt.figure(dpi=dpi, figsize=(width, height))
        self.figure.suptitle(title, fontsize=fontsize)
        return self.figure

    def add_axes(self, name, pos):
        sharey = None if not self.axes else self.axes[0]
        self.axes.append(self.figure.add_subplot(*pos, sharey=sharey))
        self.axes[-1].set_title(name)
        return self.axes[-1]

    def add_normal(self, name, pos):
        refpath = self.config.get('paths', 'normal_%s' % name)
        with open(refpath) as fh:
            mean, dev = np.loadtxt(fh, delimiter=',')
        std = dev * self.config.getint('plots', 'standardeviation')
        x = np.arange(mean.size)
        self.axes[pos].fill_between(x, mean - std, mean + std, color='k',
            alpha=0.15)
        self.axes[pos].plot(mean, color='k')

    def save(self, destpath):
        self.figure.subplots_adjust(**self.subplotparams)
        self.figure.savefig(os.path.join(destpath, self.title))
        plt.close(self.figure)


class AnglePlot(Curves):

    def __init__(self, title, **kwargs):
        super().__init__(kwargs['config'])
        self.count = 0
        self.title = title
        self.joints = []
        self.legends = {}

    def add_joint(self, name, direction, legends, curves, vlines):
        leftside = np.arange(direction.size)[direction == 0]
        rightside = np.arange(direction.size)[direction == 1]
        if not np.any(leftside) and not np.any(rightside):
            return
        self.joints.append({'name':name})
        self.joints[self.count]['sides'] = []
        if np.any(leftside):
            self.joints[self.count]['sides'].append('leftside')
            self.joints[self.count]['leftside'] = {}
            self.joints[self.count]['leftside']['curves'] = curves[leftside]
            self.joints[self.count]['leftside']['vlines'] = vlines[leftside]
            self.legends['leftside'] = legends[leftside].tolist()
        if np.any(rightside):
            self.joints[self.count]['sides'].append('rightside')
            self.joints[self.count]['rightside'] = {}
            self.joints[self.count]['rightside']['curves'] = curves[rightside]
            self.joints[self.count]['rightside']['vlines'] = vlines[rightside]
            self.legends['rightside'] = legends[rightside].tolist()
        self.ndata, __ = curves.shape
        self.count += 1

    def summary(self, pos):
        for side in self.joints[pos]['sides']:
            curves = self.joints[pos][side]['curves']
            self.joints[pos][side]['curves'] = np.mean(curves, axis=0)
            vlines = self.joints[pos][side]['vlines']
            self.joints[pos][side]['vlines'] = (np.mean(vlines, axis=0),)
            self.legends = {'leftside':['leftside',], 'rightside':['rightside',]}

    def plot(self, summary=False, putlegends=False):
        if self.joints == []:
            return
        figure = self.new_figure(self.title)
        for j, joint in enumerate(self.joints):
            ax = self.add_axes(joint['name'], (1, self.count, j+1))
            if summary:
                self.summary(j)
                self.add_normal(joint['name'], j)
                self.color = ('r', 'b')
            ax.set_prop_cycle(plt.cycler('color', self.color))
            vlinecolor = 0
            for side in self.joints[j]['sides']:
                lines = ax.plot(self.joints[j][side]['curves'].transpose())
                [l.set_label(s) for l, s in zip(lines, self.legends[side])]
                ax.axhline(0, c='k', ls='--')
                ax.set_xlabel('Ciclo [%]')
                ax.set_ylabel('Grados [°]')
                for line in self.joints[j][side]['vlines']:
                    color = self.color[vlinecolor]
                    ax.axvline(line, c=color, ls='--', lw=0.7, alpha=0.5)
                    vlinecolor += 1
        if putlegends:
            ax.legend(bbox_to_anchor=(1.05, 1))
            self.subplotparams['right'] = .85


class Table(object):
    box = {'top':0.85, 'bottom':0.05, 'left':0.03, 'right':0.97}

    def __init__(self, config, title):
        self.index = None
        self.title = title
        self.config = config
        self.nrows = 0
        self.ncols = 0
        self.colors = []
        self.subtitles = []
        self.subtables = []

    def add_normal(self, config_name, header="", formater=""):
        path = self.config.get('paths', config_name)
        with open(path) as fh:
            norm = np.loadtxt(fh, delimiter=',').round(1)
        cols = ['${}{}{}$'.format(u, formater, v) for u, v in norm.transpose()]
        self.add_subtable(header, np.array(cols).reshape(len(cols), 1), ['k',])
        self.normalflag = True

    def add_index(self, index):
        self.nrows = len(index)
        self.index = np.zeros((1 + self.nrows, 1), dtype='U32')
        self.index[1:, 0] = index

    def add_subtable(self, header, values, colcolors, title=""):
        self.ncols += len(header)
        self.colors += colcolors
        self.subtitles.append(title)
        self.subtables.append(np.vstack((header, values)))

    @property
    def xpoints(self):
        iwidth = self.config.getfloat('plots', 'cell_index_width')
        nwidth = self.config.getfloat('plots', 'cell_normal_width')
        rlindex = self.box['left'] + iwidth  # RightLineIndex
        llnormal =  self.box['right'] - nwidth
        xmiddle = np.linspace(rlindex, llnormal, self.ncols)
        xlines = np.hstack((self.box['left'],  xmiddle, self.box['right']))
        return xlines, xlines[:-1] + np.diff(xlines)*.5

    @property
    def ypoints(self):
        ylines = np.linspace(self.box['bottom'], self.box['top'], self.nrows + 2)
        return ylines, ylines[:-1] + np.diff(ylines)*.5


    def build_grid(self, fig):
        xlines, __ = self.xpoints
        ylines, __ = self.ypoints
        xbounds = xlines[np.newaxis, (0, -1)]
        ybounds = ylines[np.newaxis, (0, -1)]
        lines = []
        for level in ylines:
            l = Line2D(xbounds, (level, level), color='k',
                       transform=fig.transFigure)
            lines.append(l)
        for level in xlines:
            l = Line2D((level, level), ybounds, color='k',
                       transform=fig.transFigure)
            lines.append(l)
        fig.lines.extend(lines)

    def build_text(self, fig):
        mastertable = np.hstack((self.index, np.hstack((self.subtables))))
        textsize = np.zeros(mastertable.shape, dtype=np.int)
        textsize[:, 0] = self.config.getint('plots', 'subtitlesize')
        textsize[0, :] = self.config.getint('plots', 'subtitlesize')
        textsize[1:, 1:] = self.config.getint('plots', 'textsize')

        textcolor = np.zeros(mastertable.shape, dtype='U32')
        textcolor[:, 0] = 'k'
        for i, color in enumerate(self.colors):
            textcolor[:, i+1] = color

        __, xwords = self.xpoints
        __, ywords = self.ypoints
        for i, ycoord in enumerate(ywords[::-1]):
            for j, xcoord in enumerate(xwords):
                fig.text(xcoord, ycoord, mastertable[i, j],
                         color=textcolor[i, j],
                         fontdict={"fontsize":textsize[i,j]},
                         verticalalignment='center',
                         horizontalalignment='center')

    def build(self, figure=None):
        dpi = self.config.getint('plots', 'dpi')
        width = self.config.getint('plots', 'tablewidth')
        height = self.config.getint('plots', 'tableheight')
        fontsize = self.config.getint('plots', 'titlesize')

        if not figure:
            self.figure = plt.figure(figsize=(width, height), dpi=dpi)
            self.figure.suptitle(self.title, fontsize=fontsize)
        else:
            self.figure = figure

        self.build_grid(self.figure)
        self.build_text(self.figure)

    def save(self, destpath):
        self.figure.savefig(os.path.join(destpath, self.title))
        plt.close(self.figure)


class SpatioTemporal(Table):

    def build(self, params):
        index = ("Duración [s]", "F.Apoyo [%]", "F.Balanceo [%]",
                 "L.Zancada [m]", "Cadencia [p/min]", "Velocidad [m/s]")
        header = ("Izquierdo", "Derecho")
        paramcolors = ['r', 'b']

        self.add_index(index)
        self.add_subtable(header, params, paramcolors)
        self.add_normal('normal_stp', ('Normal [$norm \pm dev$]',), '\pm')
        super().build()


class ROM(Table):

    def build(self, params):
        index = ("Cadera", "Rodilla", "Tobillo")
        header = ("Imin", "Imax", "Dmin", "Dmax")
        paramcolors = ['r', 'r', 'b', 'b']
        self.add_index(index)
        self.add_subtable(header, params, paramcolors)
        self.add_normal('normal_rom', ("Normal [Min < Max]",), "<")
        super().build()
