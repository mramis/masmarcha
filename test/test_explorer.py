#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2019  Mariano Ramis

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
import time

from core.explorer import *
from settings import config



app_path = config.get("paths", "video")
video_path = os.path.join(app_path, "Jorge_Moviglia/281019140712.avi")

config.set("current", "source", video_path)
config.set("explorer", "empty_frame_limit", "50")


def test_explorer():

	explorer = VideoExplorer(config)

	t = time.perf_counter()
	gma = explorer.explore()

	print(list(gma.get_walks()))
	

	perf = time.perf_counter() - t
	print(f"{len(gma.index)} frames explored in {perf} seconds")
