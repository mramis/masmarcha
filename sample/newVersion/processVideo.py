#!/usr/bin/env python
# coding: utf-8

'''Docstring
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


# import os
import pickle

# from video.main import readVideo

# VIDEOFILE = os.path.abspath(
#     '/home/mariano/Escritorio/proyecto-video/Denise_Roque.mp4'
#     )
# videodata = readVideo(VIDEOFILE)

# por ahora vamos a usar la lectura de este video que está guardada en:
with open('./video/sample.txt') as samplefile:
    videodata = pickle.load(samplefile)



# tomo una muestra de la data de video porque tiene muchos cuadros
none_frames = []
for N, array in enumerate(videodata):
    if N == 100: break
    print array

