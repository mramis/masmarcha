#!/usr/bin/env python
# coding: utf-8

"""Docstring."""

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


import skvideo.io
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt


video = '/home/mariano/Descargas/VID_20170707_104121679.mp4'
video_data = skvideo.io.vreader(video, as_grey=True, num_frames=500)
# frame = video_data.next()[0].reshape((1080, 1920))
# threshold_level = 250  # esta es una variable que me gustaria controlar
# morphology = ndimage.generate_binary_structure(2, 1)
# for frame in video_data:
#     frame = frame[0].reshape((1080, 1920))
#     binary = np.where(frame > threshold_level, 1, 0)
#     structure, labels = ndimage.label(binary, morphology)
#     com = ndimage.center_of_mass(binary, structure, np.arange(1, labels + 1,))
#     y, x = np.array(com).T
    # plt.imshow(frame)
    # plt.plot(x, y)
    # plt.show()
#

# funciona pero es muy dependiente del entorno, en el caso de maxi el brillo de
# luz led del pie contralateral se mete en el filtrado. Pasa lo mismo con los
# reflejos en el vidrio. Por lo tanto en necesario generarlo en un ambiente
# controlado.


def main():
    threshold_level = 250  # esta es una variable que me gustaria controlar
    morphology = ndimage.generate_binary_structure(2, 1)
    for frame in video_data:
        frame = frame[0].reshape((1080, 1920))
        binary = np.where(frame > threshold_level, 1, 0)
        structure, labels = ndimage.label(binary, morphology)
        com = ndimage.center_of_mass(binary, structure, np.arange(1, labels + 1,))
        y, x = np.array(com).T

import cProfile

cProfile.run('main()')
