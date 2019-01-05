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


import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


# TODO: Tabla para ROM

def plot_spatiotemporal(name, params, norm, std):
    fig = plt.gcf()
    fig.set_figwidth(15)

    spatiotemporal = plt.gca()
    spatiotemporal.set_axis_off()

    lines = []

    # Primer separador vertical.
    lines.append(Line2D((.11, .11), (0.05, 0.85), transform=fig.transFigure,
        figure=fig, color='k'))

    # El resto de los separadores verticales.
    x_separator, xstep = np.linspace(.45, 0.85, 4, retstep=True)
    for p in x_separator:
        lines.append(Line2D((p, p), (0.05, 0.85), transform=fig.transFigure,
            figure=fig, color='k'))

    # Separadores horizontales.
    y_separator, ystep = np.linspace(0.05, 0.85, 8, retstep=True)
    for p in y_separator:
        lines.append(Line2D((0.11, 0.85), (p, p), transform=fig.transFigure,
            figure=fig, color='k'))

    x_wordpoints = np.linspace(.5, 0.85, 3)
    y_wordpoints = np.linspace(-0.05, 0.85, 7)[::-1]


    # Columnas
    col_names = ['Izquierdo', 'Derecho', 'Normal']
    col_colours = ['r', 'b', 'k']
    for e, word in enumerate(col_names):
        spatiotemporal.text(x=x_wordpoints[e], y=y_wordpoints[0], s=word,
            horizontalalignment='center',
            fontdict={'size':22, 'color':col_colours[e]})

    # Filas
    row_names = [
        'Duración de ciclo [seg]',
        'Fase de apoyo [%]',
        'Fase de Balanceo [%]',
        'Longitud de zancada [m]',
        'Cadencia [pasos/minuto]',
        'Velocidad media [m/seg]']

    for e, word in enumerate(row_names):
        spatiotemporal.text(x=0, y=y_wordpoints[e+1], s=word,
            fontdict={'size':23})

    # Valores
    sac = ['${}\pm{}$'.format(n, s) for n, s in zip(norm.round(), std.round())]
    left = np.asarray(params['left']).mean(0).round(2)
    right = np.asarray(params['right']).mean(0).round(2)
    data = np.stack((left, right, sac)).transpose()

    for i in range(len(row_names)):
        for j in range(len(col_names)):
            spatiotemporal.text(x=x_wordpoints[j], y=y_wordpoints[i+1],
                s=data[i, j], horizontalalignment='center',
                fontdict={'size':20, 'color':col_colours[j], })

    fig.lines.extend(lines)
    fig.suptitle('Parámetros espaciotemporales', fontsize=28)
    plt.savefig('%s-stp.png' % name)
    plt.close()


def plot_angles(name, angles, legends, side):

    lat = {'left': 'Izquierdo', 'right': 'Derecho'}
    colors = plt.cm.Spectral(np.linspace(0, 1, len(legends[side])))
    fig, (hip, knee, ankle) = plt.subplots(ncols=3, sharey=True)

    hip.set_prop_cycle(plt.cycler('color', colors))
    hip.plot(np.asarray(angles[side]['hip']).transpose())
    for v in angles[side]['phase']:
        hip.axvline(v, c='k', ls='--', lw=0.6, alpha=0.4)
    hip.axhline(0, c='k', ls='--')

    knee.set_prop_cycle(plt.cycler('color', colors))
    knee.plot(np.asarray(angles[side]['knee']).transpose())
    for v in angles[side]['phase']:
        knee.axvline(v, c='k', ls='--', lw=0.6, alpha=0.4)
    knee.axhline(0, c='k', ls='--')

    ankle.set_prop_cycle(plt.cycler('color', colors))
    ankle.plot(np.asarray(angles[side]['ankle']).transpose())
    for v in angles[side]['phase']:
        ankle.axvline(v, c='k', ls='--', lw=0.6, alpha=0.4)
    ankle.axhline(0, c='k', ls='--')

    plt.legend(loc=(1, 0.1), labels=legends[side])
    fig.suptitle('Cinemática %s N=%d' % (lat[side], len(legends[side])),
                 fontsize=22)
    fig.set_figwidth(15)
    plt.savefig('%s-Cinemática-%s.png' % (name, lat[side]))
    plt.close()


def plot_angles_summary(name, jointname, angles, norm, std, normet, dev=2):
    title = {'hip': 'Cadera', 'knee': 'Rodilla', 'ankle': 'Tobillo'}
    lim = {'hip': (-35, 45), 'knee': (-25, 85), 'ankle': (-45, 35)}

    fig = plt.figure()
    joint = plt.gca()

    # SAC
    nhip, nknee, nankle = norm
    ship, sknee, sankle = std
    norm = {'hip': nhip, 'knee': nknee, 'ankle': nankle}
    std = {'hip': ship, 'knee': sknee, 'ankle': sankle}

    joint.fill_between(np.arange(norm[jointname].size),
                       norm[jointname] - std[jointname]*dev,
                       norm[jointname] + std[jointname]*dev,
                       color='k', alpha=0.15)
    joint.plot(norm[jointname], color='k')

    # Valores
    joint.plot(np.asarray(angles['left'][jointname]).mean(0),
               c='r', label='Izquierdo')
    joint.plot(np.asarray(angles['right'][jointname]).mean(0),
               c='b', label='Derecho')
    joint.axvline(np.mean(angles['left']['phase'][1].mean()),
                  c='r', ls='--', lw=0.8, alpha=0.8)
    joint.axvline(np.mean(angles['right']['phase'][1].mean()),
                  c='b', ls='--', lw=0.8, alpha=0.8)

    joint.axvline(normet[1], c='k', alpha=0.2)
    joint.axhline(0, c='k', ls='--')
    joint.set_ylim(*lim[jointname])

    plt.legend()
    fig.set_figwidth(8)
    fig.suptitle(title[jointname], fontsize=22)
    plt.savefig('%s-%s.png' % (name, title[jointname]))
    plt.close()


def plot(source, stp, angles, legends, norm, std, normet, stdet):
    # Parametros espaciotemporales.
    plot_spatiotemporal(source, stp, normet, stdet)

    # Curvas de angulos.
    plot_angles(source, angles, legends, 'left')
    plot_angles(source, angles, legends, 'right')

    # Curvas de resumen.
    plot_angles_summary(source, 'hip', angles, norm, std, normet)
    plot_angles_summary(source, 'knee', angles, norm, std, normet)
    plot_angles_summary(source, 'ankle', angles, norm, std, normet)
