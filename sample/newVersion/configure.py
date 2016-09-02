#!/usr/bin/env python
# coding: utf-8

'''Aquí se crea el manejador del/os archivo/s de configuración de la
aplicación.
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


import os
import cPickle
import logging


class mm_config(object):
    '''Manejar las rutas de la aplicación, guardar los valores
    establecidos por defecto como por el usuario. Las rutas que se establecen:
        root-path, la dirección de la aplicación.
        work-path, el espacio de trabajo, donde se generarán los procesos.
        base-path, la dirección para guardar la base de datos.
        logg-path, la dirección de registro de actividad.

    Methods:
        __init__(root_path) toma como argumento opcional la dirección que por
        defecto va a tener la aplicación. Si no se pasa argumento se
        toma la dirección del usuario. Se definen las rutas por defecto.

        save_configuration() guarda la configuración que está en forma de
        diccionario en un archivo llamado .config que está en el root-path.
        Utiliza la librería cPickle.

        update() carga la configuración de el archivo .config, si éste existe.
        Utiliza la librería cPickle.

    '''

    def __init__(self, root_path=None):

        if not root_path:
            self._root_path = os.path.join(
                os.path.expanduser('~'), 'MasMarcha'
                )
        try:
            self.update()
            logging.info('actualización exitosa')
        except :
            logging.warning("no se pudo actualizar archivo de configuración")
            work_path = os.path.join(self._root_path, 'espacio-trabajo')
            base_path = os.path.join(self._root_path, '.base')
            logg_path = os.path.join(self._root_path, 'loggin')

            for path in self._root_path, work_path, base_path, logg_path:
                if not os.path.isdir(path):
                    os.mkdir(path)
            
            self._config_data = {
                'root-path': self._root_path,
                'work-path': work_path,
                'logg-path': logg_path,
                'base-path': base_path
                } 
        return

    @property
    def work_path(self):
        return self._config_data['work-path']

    @work_path.setter
    def work_path(self, path):
        self._config_data['work-path'] = os.path.abspath(path)

    def save_configuration(self):
        config_file = os.path.join(self._root_path, '.config')
        with open(config_file, 'w') as filewritter:
            cPickle.dump(self._config_data, filewritter)

    def update(self):
        config_file = os.path.join(self._root_path, '.config')
        with open(config_file) as filereader:
            self._config_data = cPickle.load(filereader)

if __name__ == '__main__':
    configuration = mm_config()
    configuration.work_path = '/home/mariano/Escritorio'
    configuration.save_configuration()
    print configuration.work_path
