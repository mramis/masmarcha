#!/usr/bin/env python
# coding: utf-8

'''Por el momento se me ocurre que lo mejor extraer todos los datos del video
y guardarlos en una cola, para después reacomodar los arrays cuando tenga la información para intepolar los datos faltantes.
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

NEIGHBORS = ndimage.generate_binary_structure(2,2)

def findMarkers(frame, min_markers=3):
    '''Busca marcas con el nivel mas alto de blanco alto(> .99),
    en el cuadro que se le pasa como argumento.
    '''
    gray_frame = rgb2gray(frame)
    mask = gray_frame < 1.0
    gray_frame[mask] = 0

    splitframe = roi(gray_frame)
    upper_frame = splitframe.next()
    lower_frame = splitframe.next()

    upper_labeled_frame, upper_n_markers = ndimage.label(
        upper_frame, structure=NEIGHBORS
        )
    lower_labeled_frame, lower_n_markers = ndimage.label(
        lower_frame, structure=NEIGHBORS
        )
    if lower_n_markers == min_markers:
        upper_markers_range = np.arange(1, upper_n_markers + 1)
        lower_markers_range = np.arange(1, lower_n_markers + 1)
        upper_markers_position = ndimage.center_of_mass(
                upper_frame, upper_labeled_frame, upper_markers_range
                )
        lower_markers_position = ndimage.center_of_mass(
                lower_frame, lower_labeled_frame, lower_markers_range
                )
        markers_position = np.array((upper_markers_position,
                                     lower_markers_position))
    else:
        markers_position = None
    return markers_position

def readVideo(filename, fps=24):
    
    video = skvideo.io.vreader(filename, inputdict={'-r':str(fps)})
    markers = deque(maxlen=5000)

    for frame in video:
        markers.appendleft(findMarkers(frame))

    return markers


if __name__ == '__main__':
    import os
    import pickle

    test = os.path.abspath(
            '/home/mariano/Escritorio/proyecto-video/Denise_Roque.mp4'
            )

    with open('sample.txt', 'w') as fh:
        pickle.dump(readVideo(test), fh)


