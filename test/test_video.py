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


import time
import queue
import threading

from src.core.videoio import VideoReader, VideoWriter
from src.core.settings import config


def test_videoreader():
    reader = VideoReader(config)

    config.set("current", "source", "0")
    reader.find_source()

    reader.open()
    reader.read()


def test_videowriter():
    writer = VideoWriter(config)

    writer.open()
    writer.write()

    writer.sqlite_insert_video()


def test_thread_execution():

    reader = VideoReader(config)
    writer = VideoWriter(config)

    q = queue.Queue(maxsize=1)
    e = threading.Event()

    reader.start_thread(q, e)
    writer.start_thread(q, e)

    time.sleep(3)
    e.set()
