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


from os import path
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy as np


style.use('seaborn')

LIMITS = {
    'Cadera': (-30, 50),
    'Rodilla': (-20, 85),
    'Tobillo': (-40, 30)}


class CyclerPlot(object):

    def __init__(self, fig, label, cfg):
        self.dirpath = cfg.get('paths', 'splots')
        self.phthres = cfg.getfloat('engine', 'phasethreshold')
        self.label = label
        self.fig = fig
        self.ax = fig.add_subplot(1, 1, 1)
        self.ax.set_ylabel(u'Velocidad de marcadores')


    def plot_cycler_outcome(self, diff, mov):
        M5, M6 = diff.transpose()
        stance = np.arange(mov.size)[np.bool8(mov*-1 + 1)]
        swing = np.arange(mov.size)[mov]
        self.ax.plot(M5)
        self.ax.plot(M6)
        self.ax.plot(swing, np.repeat(-1, swing.size), 'gs')
        self.ax.plot(stance, np.repeat(-1, stance.size), 'rs')
        self.ax.axhline(self.phthres, color='k', linestyle='--', linewidth=1.0)
        self.ax.legend(('M5', 'M6', 'balanceo', 'apoyo', 'umbral fase'))

    def draw_text(self):
        text = """Se muestran los resultados del proceso de detectar
        ciclos dentro de la caminata. la amplitud del filtro de
        cambio de fase ({0}) es la velocidad que se considera como límite
        de cambio de fase."""
        text = ' '.join(s.strip() for s in text.split())
        self.fig.text(0.035, 0.25, text.format(self.phthres), fontsize=8,
            style='oblique', ha='left', va='top', wrap=True)

    def save(self, withtext=True):
        if withtext:
            self.draw_text()
        self.ax.set_xticks([])
        self.fig.suptitle(self.fig.get_label(), y=0.95)
        self.fig.legend(fontsize=8)
        self.fig.savefig('%s.png' % path.join(self.dirpath, self.label))


class JointPlot(object):

    def __init__(self, fig, label, limits, cfg):
        self.dirpath = cfg.get('paths', 'splots')
        self.label = label
        self.fig = fig
        self.ax = fig.add_subplot(1, 1, 1)
        self.ax.set_xlabel(u'% Ciclo')
        self.ax.set_ylabel(u'° Grados')
        self.ax.set_ylim(limits)
        self.sactext = ''

    def add_cycle(self, angles, switch, label=None):
        self.ax.plot(np.arange(angles.size), angles, label=label, alpha=0.7)
        self.ax.axvline(switch, color='k', ls='--', lw=0.3, alpha=0.5)

    def draw_sac(self, mean, std, switch, n):
        x = np.arange(mean.size)
        self.ax.fill_between(x, mean+std*2, mean-std*2, color='k', alpha=0.1)
        self.ax.fill_between(x, mean+std, mean-std, color='k', alpha=0.2)
        self.ax.axvline(switch, color='k', lw=0.5, alpha=0.8)
        self.ax.plot(x, mean, color='k', lw=1.5)
        self.sactext = """En negro se dibuja el valor medio de marcha sin
        alteración clínica (sac), el sombreado gris representa dos desviaciones
        estándar (95%). N={}.""".format(n)

    def draw_text(self):
        basictext = """Cinemática articular en plano sagital. En negativo
        valores de extensión, en positivo valores de flexión. En punteado
        vertical se muestra el momento de cambio de fase de apoyo a fase de
        balanceo."""
        text = ' '.join(s.strip() for s in (basictext + self.sactext).split())
        self.fig.text(0.03, 0.15, text, fontsize=8, style='oblique', ha='left',
            va='top', wrap=True)

    def save(self, withtext=False):
        if withtext:
            self.draw_text()
        self.ax.axhline(0, color='k', linestyle='--', linewidth=1.0)
        self.fig.suptitle(self.fig.get_label(), y=0.95)
        self.fig.legend(fontsize=8)
        self.fig.savefig('%s.png' % path.join(self.dirpath, self.label))


class STPlot(object):

    def __init__(self, fig, cfg):
        self.dirpath = cfg.get('paths', 'splots')
        self.fig = fig
        self.ax = fig.add_subplot(1, 1, 1)
        self.ax.axis('off')
        self.maxitem = 14
        self.params = []
        self.sactext = ''

    def add_cycle(self, parameters):
        self.params.append(parameters)

    def draw_text(self):
        basictext = """Resumen de {0} ciclos. En orden de izquierda a derecha
        duración del ciclo en segundos, porcentaje de fase de apoyo,
        porcentaje de fase de balanceo, longitud de zancada en metros, cadencia
        en pasos por minuto y velocidad media en metros por segundo."""
        basictext = basictext.format(len(self.params))
        text = ' '.join(s.strip() for s in (basictext + self.sactext).split())
        self.fig.text(0.03, 0.25, text, fontsize=8,style='oblique', ha='left',
            va='top', wrap=True)

    def sumarize(self):
        Y = np.array(self.params)
        table = (['MAX', ] + Y.max(axis=0).round(2).tolist(),
                 ['MIN', ] + Y.min(axis=0).round(2).tolist(),
                 ['PROMEDIO', ] + Y.mean(axis=0).round(2).tolist(),
                 ['ERROR STD', ] + Y.std(axis=0).round(2).tolist())
        return(table)

    def build_table(self):
        cols = [u'', u'D [s]', u'A [%]', u'B [%]',
                u'Z [m]', u'C [pasos/min]', u'V [m/s]']
        self.ax.table(loc='center', cellLoc='center', colLoc='center',
            colLabels=cols, cellText=self.sumarize())

    def save(self, withtext=False):
        label = self.fig.get_label()
        if withtext:
            self.draw_text()
        self.build_table()
        self.fig.suptitle(label, y=0.75)
        self.fig.tight_layout()
        self.fig.savefig('%s.png' % path.join(self.dirpath, label))


class Plotter(object):

    plots = defaultdict(dict)

    def __init__(self, cfg):
        self.cfg = cfg
        self.aspect = cfg.getfloat('plots', 'aspect')
        self.dpi = cfg.getint('plots', 'dpi')

    def new_figure(self, label):
        fig = plt.figure(figsize=plt.figaspect(self.aspect), dpi=self.dpi)
        fig.set_label(label)
        fig.subplots_adjust(bottom=0.3)
        self.plots[label]['fig'] = fig
        return(fig)

    def new_cycler_plot(self, label):
        fig = self.new_figure(label)
        ax = CyclerPlot(fig, label, self.cfg)
        self.plots[label]['ax'] = ax
        return(ax)

    def new_joint_plot(self, label):
        fig = self.new_figure(label)
        ax = JointPlot(fig, label, LIMITS[label], self.cfg)
        self.plots[label]['ax'] = ax
        return(ax)

    def new_table_plot(self):
        label = u'Parámetros espacio-temporales'
        fig = self.new_figure(label)
        ax = STPlot(fig, self.cfg)
        self.plots[label]['ax'] = ax
        return(ax)

    def auto(self):
        self.autobuild_joints()
        self.new_table_plot()
        return(self)

    def autobuild_joints(self):
        for joint in ('Cadera', 'Rodilla', 'Tobillo'):
            self.new_joint_plot(joint)

    def add_cycle(self, cid, spacetemporal, angles, withlabels=False):
        label = None
        for i, joint in enumerate(('Cadera', 'Rodilla', 'Tobillo')):
            ax = self.plots[joint]['ax']
            if withlabels:
                label = cid
            ax.add_cycle(angles[i], spacetemporal[1], label)
        ax = self.plots[u'Parámetros espacio-temporales']['ax']
        ax.add_cycle(spacetemporal)

    def add_cycler(self, wid, diff, mov):
        ax = self.new_cycler_plot(wid)
        ax.plot_cycler_outcome(diff, mov)

    def with_sac(self):
        sacpath = self.cfg.get('paths', 'sac')
        sac = dict(np.load(sacpath).items())
        mangles = sac['mean_angles']
        sangles = sac['std_angles']
        switch = sac['mean_spacetemporal'][1]
        for i, joint in enumerate(('Cadera', 'Rodilla', 'Tobillo')):
            ax = self.plots[joint]['ax']
            ax.draw_sac(mangles[i], sangles[i], switch, sac['nsample'])

        # ax = self.plots[u'Parámetros espacio-temporales']['ax']
        # ax.add_cycle(spacetemporal)


    def saveplots(self, withtext=False):
        for __, plot in self.plots.items():
            plot['ax'].save(withtext)




#     def add_sac(self, sac):
#         stext = """En color negro se muestra el valor promedio (N={n}) de las
#             muestras de personas sin alteración clínica (SAC), en sombreado
#             gris el desvío estandar."""
#         if self.joints:
#             for i, (joint, (__, ax, text)) in enumerate(self.joints.items()):
#                 mean, std, nsac = sac[i]
#                 ax.fill_between(np.arange(mean.size), mean-std, mean+std,
#                     color='k', alpha=.3)
#                 # El sombreado del desvío estandar se dibuja primero.
#                 poly = ax.lines.pop()
#                 ax.lines.insert(0, poly)
#                 ax.plot(mean, color='k', linewidth=1.5)
#                 text += stext.format(n=nsac)
#
