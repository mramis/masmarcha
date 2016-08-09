#!/usr/bin/env python
# coding: utf-8

'''Por el momento se me ocurre que lo mejor extraer todos los datos del video
y guardarlos en una cola, para después reacomodar los arrays cuando tenga la
información para intepolar los datos faltantes.
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

from collections import deque

import skvideo.io
import numpy as np
from skimage.color import rgb2gray
from scipy import ndimage

from frame import roi

NEIGHBORS = ndimage.generate_binary_structure(2, 2)


def controlFrame(var, collection):
    pass


def findMarkers(frame, expected=(2, 3)):
    '''Busca marcas con el nivel mas alto de blanco alto(> .99),
    en el cuadro que se le pasa como argumento.
    '''
# se convierte a escalas de grises el cuadro en rgb, y luego se binariza la
# imagen, todo lo que no es "marcador(blanco=1.0)" se vuelve negro(0.0)
    gray_frame = rgb2gray(frame)
    mask = gray_frame < 1.0
    gray_frame[mask] = 0

# se divide la imagen en dos regiones de interés, el cuadro superior, y el
# inferior, en teoria se podría elegir cualquier sector de la imagen, cuestión
# que aceleraría el proceso de búsqueda!. En el cuadro superior se busca el
# tronco y la cadera, y en el inferior la rodilla, tobillo y pie.
# Todos los datos perdidos pueden interpolarse que se registren como perdidos
# pueden ser interpolados por una línea recta en un posterior análisis.
    splitframe = roi(gray_frame)
    upper_frame = splitframe.next()
    lower_frame = splitframe.next()

    upper_labeled_frame, upper_n_markers = ndimage.label(
        upper_frame, structure=NEIGHBORS
        )
    lower_labeled_frame, lower_n_markers = ndimage.label(
        lower_frame, structure=NEIGHBORS
        )

# si la cantidad de marcadores en el cuadro inferior es igual a la esperada, y
# hasta el momento en que se escribe esta línea es de 3 marcadores, entonces 
# se habilita la búsqueda de los centros de masa de los marcadores y se
# exportan como tuplas de dos listas, la del cuadro superior en [0] y la del
# cuadro superior en [1].
# En el caso en que haya más de los marcadores esperados en alguno de los dos
# cuadros, se descarta el frame y se registra como "sobrecargado" por reflejos
# indeseados.
# en el caso en que aparecen menos marcadores de los esperados en el cuadro
# inferior el cuadro se registra como "None".
    if lower_n_markers == expected[1]:
        upper_markers_range = np.arange(1, upper_n_markers + 1)
        lower_markers_range = np.arange(1, lower_n_markers + 1)
        upper_markers_position = ndimage.center_of_mass(
            upper_frame,
            upper_labeled_frame,
            upper_markers_range
            )
        lower_markers_position = ndimage.center_of_mass(
            lower_frame,
            lower_labeled_frame,
            lower_markers_range
            )
        markers_position = (upper_markers_position, lower_markers_position)
    elif upper_n_markers > expected[0] or lower_n_markers > expected[1]:
# la sobrecarga se produce por el reflejo de los marcadores en superficies
# pulidas y, en algunos casos, por la baja frecuencia de captura.
        markers_position = 'SOBRECARGA'
        print 'ADVERTENCIA: Sobrecarga de marcadores en la imagen'
    else:
        markers_position = None
    return markers_position


def readVideo(filename, fps=24):

    video = skvideo.io.vreader(filename, inputdict={'-r': str(fps)})
    markers = deque(maxlen=5000)

# se realiza una selección de los cuadros cuando el marker returna el valor
# de None; para no extender la cola de guardado de markadores, cuando el valor
# es none 5 veces consecutivas, se saltean los cuadros hasta que vuelva a haber
# un valor distinto. Lo ideal sería que el soft no tenga que pasar por el
# filtrado de cada cuadro si no está la imagen, pero eso no puede saberse de 
# otra forma, al menos no se me ocurre hasta ahora.
    frame_false = 0
    for frame in video:
        marker = findMarkers(frame)
        if marker is None:
            frame_false += 1
            if frame_false > 5:
                continue
            markers.appendleft(marker)
        else:
            frame_false = 0
            markers.appendleft(marker)

    return markers


if __name__ == '__main__':
    import os
    import pickle

    test = os.path.abspath(
        '/home/mariano/Escritorio/proyecto-video/Denise_Roque.mp4'
        )

    with open('sample.txt', 'w') as fh:
        pickle.dump(readVideo(test), fh)
