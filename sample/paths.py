#!usr/bin/env python
# coding: utf-8

'''This module create the App folders
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

import os
import shutil
import datetime

# si la aplicación se corre desde otro directorio lo que sigue abajo carece de
# sentido y se genera un error en las direcciones
SAMPLEAPP = os.path.abspath('.')
REPORTDIRECTORY = os.path.join(SAMPLEAPP, 'documento')
IMAGESDIRECTORY = os.path.join(REPORTDIRECTORY, 'images')
TIPOGRAPHYSDIRECTORY = os.path.join(REPORTDIRECTORY, 'tipografias')

HOME = os.path.expanduser('~')
ANGULOSAPPDIRECTORY = os.path.join(HOME, 'AngulosApp')
CASEDIRECTORY = os.path.join(ANGULOSAPPDIRECTORY, 'Casos')
BASEDIRECTORY = os.path.join(ANGULOSAPPDIRECTORY, 'Bases')
TEMPDIRECTORY = os.path.join(ANGULOSAPPDIRECTORY, '.temp')


def checkPaths():
    '''Revisa que existan las rutas definidas de la aplicación, y si no es así,
        en el caso de que el programa se ejecute por primera vez, o que por
        descuido, hayan sido eliminadas; se crean los directorios.
    Args:
        None
    Returns:
        None
    '''
    paths = ANGULOSAPPDIRECTORY, CASEDIRECTORY, BASEDIRECTORY, TEMPDIRECTORY
    for path in paths:
        if not os.path.isdir(path):
            os.mkdir(path)

def casePath(name='anonimous'):
    '''Crea el directorio donde se van a guardar los resultados del proceso de
        los archivos de Kinovea ouput plain/text, si este ya no existe.
    Args:
        name: el nombre del directorio a crear.
    Returns:
        path_name: la dirección que se está buscando. 
    '''
    path_name = os.path.join(CASEDIRECTORY, name)
    if not os.path.isdir(path_name):
        os.mkdir(path_name)
    return path_name

def copyToBase(files, name='anonimous', comment=''):
    '''Hace una copia de los archivos que se le pasan a través de una lista 
        dirección de la base de datos. Si el archivo ya existe en el directorio
        será reemplazado. Además se crea un archivo de registro por cada vez que
        se lanza la aplicación, en el se escriben la fecha, alguna reseña
        (opcional), y los nombres de los archivos que fueron utilizados en la
        lectura.

    Args:
        files: Lista(list) de direcciones(absolute_paths) de los archivos que
            son la entrada a la aplicación (Kinovea output plain/text).
        name: default('anonimous'), es el nombre del directorio dentro de Bases
            donde se van a guardar las copias de los archivos utilizados en la
            lectura.
        comment: default(''), es la reseña que se escribe en el archivo de registro
            de la actividad.
    Returns:
        None.
    '''
    path_name = os.path.join(BASEDIRECTORY, name)
    if not os.path.isdir(path_name):
        os.mkdir(path_name)

    for f in files:
        shutil.copy2(f, path_name)

    record_file = os.path.join(path_name, '_registro_.txt')
    today = datetime.datetime.today().strftime('%d-%m-%Y %H:%M')
    with open(record_file, 'a') as fh:
        fh.write('Fecha: {}\n'.format(today))
        fh.write('Reseña: {}\n'.format(comment))
        fh.write('Archivos: {}\n\n'.format(str(files)))

def clearTemp(dst_path):
    '''Mueve los archivos(las gráficas de los ángulos) que se encuentran en el
    directorio temporal de la aplicación al directorio de destino que se pasa
    como argumento.
    Args:
        path de destino.
    Returns:
        None
    '''
    for graph in os.listdir(TEMPDIRECTORY):
        graph_path = os.path.join(TEMPDIRECTORY, graph)
        shutil.copy(graph_path, dst_path)
        os.remove(graph_path)

if __name__ == '__main__':
    
    checkPaths()
    copyToBase(['process.py', 'paths.py'], comment='pequeño reporte')
