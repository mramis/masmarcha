#!/usr/bin/env python3
# coding: utf-8

"""MasMarcha es una herramienta que obtine parámetros cinemáticos de la marcha
humana en el plano sagital.
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
import sys
import argparse
import json
from collections import defaultdict
from configparser import ConfigParser

from setup import check_paths, INI
from src.video import play, draw_markers, draw_rois
from src.engine import VideoEngine, KinoveaTrayectoriesEngine


check_paths()

argparser = argparse.ArgumentParser(prog='masmarcha', argument_default=None,
description=u"""Cálculo de parámetros cinemáticos de la marcha en el
plano sagital.""")

argparser.add_argument('-p', '--preview', nargs='+', help="""Toma el archivo de
    video que se especifica como ruta y lo muestra con los marcadores que se
    detectan. Modo de uso: -p /ruta/hacia/archivo.mp4. Los argumentos con valor
    que se pueden pasar son: pausetime, draw[rois, markers]. ej "-p
    /ruta/archivo.avi pausetime=0.05 draw=rois".""")

argparser.add_argument('-s', '--session', action='append',
    help=u"""Toma el archivo que se especifica como ruta y lo procesa. Por el
    momento solo archivos de video y extensiones de kinovea en texto son
    soportados. Modo de uso: -s /ruta/hacia/archivo.mp4. Pueden agregarse mas
    de un archivo con la acción repetida de "-s /ruta/hacia/archivo.mp4".""")

shell_args = argparser.parse_args()

# Lectura de configuración.
config = ConfigParser()
config.read(INI)
schema = json.load(open(config.get('paths', 'schema')))

# Ejecución de comandos de shell.
# PREVIEW:
if shell_args.preview:
    path = shell_args.preview[0]
    if not os.path.isfile(path):
        print('No existe archivo: %s' % path)
        sys.exit()
    # Lectura de los arguementos con valor arg=valor.
    extra = {k: v for k, v in (s.split('=') for s in shell_args.preview[1:])}
    # Selección de función de dibujo. Por defecto marcadores.
    if 'draw' in extra.keys():
        draw = {'rois': draw_rois, 'markers': draw_markers}[extra['draw']]
    else:
        draw = draw_markers
    # La configuración de la función de reproducción por defecto.
    kwargs = {
        'filepath': path,
        'pausetime': 0.2,
        'dfunction': draw,
        'markers': None,
        'wichone': -1,
        'regions': None,
        'schema': schema}
    kwargs.update(extra)
    play(**kwargs)
# PROCESAMIENTO Y OEBTENCIÓN DE DATOS PRIMARIOS.
if shell_args.session:
    # se decide el motor según la extensión de cada archivo.
    files = defaultdict(list)
    for filepath in shell_args.session:
        if not os.path.isfile(filepath):
            continue
        path, ext = os.path.splitext(filepath)
        files[ext].append(''.join((path, ext)))

    engine = None
    if '.txt' in files.keys():
        engine = KinoveaTrayectoriesEngine(config)
        engine.search_for_walks(files['.txt'])
        engine.dump_walks(config.get('paths', 'session'))
    elif '.avi' in files.keys():
        engine = VideoEngine(config)
        engine.search_for_walks(files['.avi'].pop(0))
    elif '.mp4' in files.keys():
        engine = VideoEngine(config)
        engine.search_for_walks(files['.mp4'].pop(0))


# parser.add_argument('-g', '--graficar', help=u"""Genera gráficas de los
#         parámetros de cinemática de la persona que se indica.""")
#
# parser.add_argument('-r', '--grabarvideo', nargs='*', help=u"""Genera un
#         archivo de video. Los argumentos con nombre obligatorios son "name",
#         y "duration". Los argumentos con nombre opcionales son "fps" y
#         "size".""")
#
# parser.add_argument('-s', '--salvarsesion', help=u"""Guarda los resultados de
#         las sesión actual en la base de datos.""")
#
# parser.add_argument('-v', '--version', action='version', help=u"""Muestra la
#         version actual del software.""", version='%(prog)s 1.0')
#
# parser.add_argument('-p', '--vistaprevia', nargs='?', const="marcadores",
#         help=u"""Muestra una vista previa del video que se va a procesar.""")
