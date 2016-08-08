#!/usr/bin/env python
# coding: utf-8

'''Clase que utiliza los paquetes de numpy (as np) y matplotlib.pyplot (as plt)
para generar las gráficas articulares.
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

class AnglePlot(object):
    '''Generación de gráficos Articulares, pueden representarse más de un
        arreglo de datos articulares en el mismo gráfico. El método
        AnglePlot.buildTimeAnglePlot recibe los datos a graficar, y puede
        usarse más de una vez hasta que se llama a los métodos
        ``AnglePlot.showPlot`` o ``AnglePlot.savePlot``.

        >>> miplot = AnglePlot('Mariano.123')

    Args:
        filename: el nombre del archivo con el que se va guardar el gráfico
        final (png file).
    Returns:
        ``AnglePlot instance``.
    '''

    def __init__(self, filename):
        self._filename = filename
        self._legends = []
        self._colors = plt.get_cmap('hsv')

    def configure(self, ylimits=None):
        '''Configura los parámetros gráficos con un diseño especial (ver
        plotParams.py

            >>> miplot.conigure(ylimtis=(-20, 50)) # cadera sin problemas

        Args:
            tupla de do elementos que establecen los límites súperior e
                inferior (eje y). Defecto: ylimits=(0, 100)
        Returns:
            ``None``.
        '''
        plotParams.personalizePlot(
                u'Ciclo', u'-Extensión / +Flexión',
                xlim=(0, 100), ylim=ylimits
        )

    def buildTimeAnglePlot(self, Angles, X=None, poly_fit=False, name=''):
        '''Construye la gráfica de ángulos que se le pasa como argumento de
            ``matplotlib.pyplot.plot``.
        
            >>> miplot.buildTimeAnglePlot(Y_HipAngles, name='hip_angles')

        Args:
            Angles: ``np.array`` que contiene los ángulos de una determinada
                articulación.
            name: ``string``, es el nombre del arreglo(si lleva uno), que se
                está generando.
        Returns:
            ``None``.
        '''        
        self._legends.append(name.decode('utf_8'))
        color = self._colors.__call__(np.random.random())
        plt.plot(Angles, linestyle='-', color=color, linewidth='4.5')
       

    def showPlot(self):
        '''Muestra la gráfica que se creo si se llamó antes al método 
        ``buildTimeAnglePlot``. Además se reinicia el objeto ``Figure`` de
        matplotlib, es decir, una vez que se llama, se pierde la gráfica creada.
            
            >>> miplot.showPlot()
        
        Returns:
            None.
        '''
        plt.legend(
                self._legends, fontsize='x-small', numpoints=1,
                fancybox=True, framealpha=.5, borderaxespad=1, ncol=3
        )
        plt.axhline(0, linestyle='--', linewidth=.7, color='0.1')
        plt.show()
        plt.close()

    def savePlot(self):
        '''Guarda la gráfica que genera el método ``buildTimeAnglePlot`` en el
        con formato .png en el directorio corriente bajo el nombre que se le
        pasa como argumento al iniciar este objeto. Además reinicia el objeto
        ``Figure`` de matplotlib.

            >>> miplot.savePlot()

        Returns:
            ``None``.
        '''
        plt.legend(
                self._legends, fontsize='x-small', numpoints=1,
                fancybox=True, framealpha=.5, borderaxespad=1, ncol=2
        )
        plt.axhline(0, linestyle='--', linewidth=.7, color='0.1')
        plt.savefig('{}.png'.format(self._filename))
        plt.close()

if __name__ == '__main__':

    miplot = AnglePlot('test.png')
    miplot.configure(ylimits=(-20, 100))
    miplot.buildTimeAnglePlot(np.power(np.arange(10), 2), name='cuadrática')
    miplot.buildTimeAnglePlot(np.power(np.arange(10), 3), name='cúbica')
    miplot.showPlot()



