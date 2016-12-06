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
from datetime import date


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

        clean_loggfiles(antique) se encarga de revisar la antigüedad de los
        archivos loggin, y si estos son mayores a los especificados en antique(
        que por defecto es 30 días) entonces son eliminados. Utiliza las
        librerias: datetime, os.

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
                    logging.info('se creó la dirección %s' % path)
            
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
        logging.info('Se cambia el espacio de trabajo a %s' % path)

    def save_configuration(self):
        config_file = os.path.join(self._root_path, '.config')
        with open(config_file, 'w') as filewritter:
            cPickle.dump(self._config_data, filewritter)

    def update(self):
        config_file = os.path.join(self._root_path, '.config')
        with open(config_file) as filereader:
            self._config_data = cPickle.load(filereader)

# creo que esto no debería estar acá! no es un archivo de configuración.
    def clean_loggfiles(self, antique=30):
        today = date.today()
        logg_path = self._config_data['logg-path']
        for logg in os.listdir(logg_path):
            logg_timestamp = os.stat(os.path.join(logg_path, logg))[-1]
            logg_born = date.fromtimestamp(logg_timestamp)
            if today.toordinal() - logg_born.toordinal() > antique:
                os.remove(os.path.join(logg_path, logg))

if __name__ == '__main__':
    configuration = mm_config()
    configuration.save_configuration()
    configuration.clean_loggfiles(5)
