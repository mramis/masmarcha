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


def joint_plot(joint, angles, cfg, labels):
    for a in angles:
        plt.plot(np.arange(a.size), a)
    plt.legend(labels)
    plt.savefig('%s.png' % path.join(cfg.get('paths', 'splots'), joint))
    plt.close()



def cycler_plot(walk, cfg):
    u"""."""
    dpi = cfg.getint('plots', 'dpi')
    width = cfg.getint('plots', 'width')
    height = cfg.getint('plots', 'height')

    fig = plt.figure(figsize=(width, height), dpi=dpi)
    fig.suptitle(str(walk), fontsize=24)

    fig_description = """Se muestran los resultados del proceso de detectar
        ciclos dentro de la caminata {id} de {source}. Las líneas M5 y M6 son
        la velocidad de los marcadores colocados en el pie. La banda de color
        rojo representa a la fase de apoyo y la banda de color verde a la fase
        de balanceo.""".format(id=walk.id, source=walk.source)

    fig_description = ' '.join(s.strip() for s in fig_description.split())

    ax = plt.subplot2grid((4, 1), (0, 0), rowspan=3)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylabel('Velocidad')
    textbox = plt.subplot2grid((4, 1), (3, 0))
    textbox.set_axis_off()

    m5, m6 = walk.diff.transpose()
    xmov = np.arange(walk.mov.size)[walk.mov]
    xnomov = np.arange(walk.mov.size)[np.bool8(walk.mov*-1 + 1)]

    ax.plot(m5)
    ax.plot(m6)
    ax.plot(xmov, np.repeat(-1, xmov.size), 'gs')
    ax.plot(xnomov, np.repeat(-1, xnomov.size), 'rs')
    ax.legend(('M5', 'M6'))

    textbox.text(-0.11, 0.35, fig_description, fontsize=8, style='oblique',
                 ha='left', va='top', wrap=True)

    plt.savefig('%s.png' % path.join(cfg.get('paths', 'splots'), str(walk)))



class JointPlot(object):

    def __init__(self, fig, label, limits, cfg):
        self.dirpath = cfg.get('paths', 'splots')
        self.label = label
        self.fig = fig
        self.fig.subplots_adjust(bottom=0.3)
        self.ax = fig.add_subplot(1, 1, 1)
        self.ax.set_xlabel(u'% Ciclo')
        self.ax.set_ylabel(u'° Grados')
        self.ax.set_ylim(limits)
        self.sactext = ''

    def add_cycle(self, angles, switch, label=None):
        self.ax.plot(np.arange(angles.size), angles, label=label, alpha=0.7)
        self.ax.axvline(switch, c='k', ls='--', lw=0.3, alpha=0.5)

    def draw_text(self):
        basictext = """Cinemática articular en plano sagital. En negativo
        valores de extensión, en positivo valores de flexión. En punteado
        vertical se muestra el momento de cambio de fase de apoyo a fase de
        balanceo."""
        text = ' '.join(s.strip() for s in (basictext + self.sactext).split())
        self.fig.text(0.03, 0.15, text, fontsize=8,style='oblique', ha='left',
            va='top', wrap=True)

    def save(self, withtext=False):
        if withtext:
            self.draw_text()
        self.ax.axhline(0, color='k', linestyle='--', linewidth=1.0)
        self.fig.legend(fontsize=8)
        self.fig.savefig('%s.png' % path.join(self.dirpath, self.label))


class STPlot(object):

    def __init__(self, fig, label, limits, cfg, *args, **kwargs):
        self.dirpath = cfg.get('paths', 'splots')
        self.label = label
        self.fig = fig
        self.fig.subplots_adjust(bottom=0.3)
        self.ax = fig.add_subplot(1, 1, 1)
        self.ax.set_xlabel(u'% Ciclo')
        self.ax.set_ylabel(u'° Grados')
        self.ax.set_ylim(limits)
        self.sactext = ''

# # def spacetemporal_plot(sptemp_data, cfg, boxplot=False):
# #     u"""."""
# #
# #     table_rows = [u'Muestra', u'Duración', u'Apoyo', u'Balanceo',
# #                   u'Zancada', u'Cadencia', u'Velocidad']
# #
# #     figsize = map(int, cfg.get('drawparams', 'figsize').split(','))
# #     dpi = cfg.getint('drawparams', 'dpi')
# #
# #     fig = plt.figure(figsize=figsize, dpi=dpi)
# #     fig.suptitle(u'Parámetros espacio-temporales', fontsize=24)
# #     fig.subplots_adjust(hspace=0.12)
# #
# #     table = plt.subplot2grid((2, 6), (0, 0), colspan=6)
# #     table.axis('off')
# #     table.table(loc='center', cellLoc='center',
# #                 colLoc='left', rowLabels=table_rows,
# #                 cellText=sptemp_data.round(2),
# #                 colColours=COLORMAP[:sptemp_data.shape[1]])
# #
# #     if boxplot:
# #         for iparam in range(6):
# #             ax = plt.subplot2grid((2, 6), (1, iparam))
# #             ax.boxplot(sptemp_data[1:, iparam],
# #                        labels=(table_rows[1:][iparam],),
# #                        showmeans=True)
# #
# #     plt.tight_layout()
# #     plt.show()


class Plotter(object):

    plots = defaultdict(dict)

    def __init__(self, cfg):
        self.cfg = cfg

    def new_figure(self, label):
        fig = plt.figure()
        fig.set_dpi(self.cfg.getint('plots', 'dpi'))
        fig.set_figwidth(self.cfg.getint('plots', 'width'))
        fig.set_figheight(self.cfg.getint('plots', 'height'))
        fig.set_label(label)
        fig.suptitle(label)
        self.plots[label]['fig'] = fig
        return(fig)

    def new_joint_plot(self, label):
        fig = self.new_figure(label)
        ax = JointPlot(fig, label, LIMITS[label], self.cfg)
        self.plots[label]['ax'] = ax
        return(ax)

    def auto(self):
        self.autobuild_joints()
        return(self)

    def autobuild_joints(self):
        for joint in ('Cadera', 'Rodilla', 'Tobillo'):
            self.new_joint_plot(joint)

    def add_cycle(self, parameters, withlabels=False):
        label = None
        for i, joint in enumerate(('Cadera', 'Rodilla', 'Tobillo')):
            ax = self.plots[joint]['ax']
            if withlabels:
                label = parameters[0]
            ax.add_cycle(parameters[2][i], parameters[1][1], label)

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
