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


import skvideo.io
import numpy as np
from skimage.color import rgb2gray
import matplotlib.pyplot as plt

from frameclassifier import classifier
from interpolation import linear_interpolation_range
# from markers import markerscollections



def findMarkers(frame, expected=(2, 3), stats=False):
    '''Busca marcas con el nivel mas alto de blanco alto(> .99),
    en el cuadro que se le pasa como argumento.
    '''
    gray_frame = rgb2gray(frame)
    mask = gray_frame < 1.0
    gray_frame[mask] = 0

    # por ahora se va a generar una división rígida del cuadro de video, cuando
    # se pueda modificar según necesidades especiales se hará.

    middle = gray_frame.shape[0] / 2
    upper_frame = gray_frame[:middle, :]
    lower_frame = gray_frame[middle:, :]
    upper_markers = classifier(upper_frame, 2)
    lower_markers = classifier(lower_frame, 3)

    # print np.array((upper_markers, lower_markers))
    return upper_markers, lower_markers


def readVideo(filename, fps=24):

    video = skvideo.io.vreader(filename, inputdict={'-r': str(fps)})
    # upper_markers_frame = markerscollections()
    # lower_markers_frame = markerscollections()
    arreglo = []
    seguro = None  # es la ultima con datos
    n_sin_cuadros = 0
    for n, frame in enumerate(video): #__ in xrange(200):
        #frame = video.next()
        markers = findMarkers(frame)[1]
        # upper_markers_frame.introduce(markers[0])
        # lower_markers_frame.introduce(markers[1])
        if not markers.any():
            n_sin_cuadros += 1
        else:
            if n_sin_cuadros != 0:
                interpolados = linear_interpolation_range(seguro, markers, n_sin_cuadros)
                n_sin_cuadros = 0
                for a in interpolados:
                    arreglo.append(a)
            arreglo.append(markers)
            seguro = markers
        if n == 100:
            break
    print [n.shape for n in arreglo]

    # upper_markers_frame.dump('test.txt')
    # lower_markers_frame.dump('testII.txt')



if __name__ == '__main__':
    import os
    import pickle

    test = os.path.abspath(
        '/home/mariano/Escritorio/proyecto-video/Giustina_final.mp4'
        )


    data_from_video = readVideo(test)
