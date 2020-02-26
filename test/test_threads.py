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
import logging
import threading

from core.threads import Producer, Consumer


logging.basicConfig(level=logging.DEBUG, format='[%(levelname)-s] %(message)s')


def test_main():
    t1 = time.perf_counter()

    q1 = queue.Queue(maxsize=5)
    e1 = threading.Event()

    p = Producer()
    c = Consumer()

    threads = [p, c]

    for t in threads:
        t.start_thread(q1, e1)

    for t in threads:
        t.join_thread()

    t2 = time.perf_counter()

    print(f"Finalizado en {t2-t1} segundos")
