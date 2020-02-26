#!/usr/bin/env python3
# coding: utf-8

"""Docstring."""

# Copyright (C) 2018  Mariano Ramis

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
import random
import logging
import threading


class Producer:
    nproduce = 0

    def __init__(self, name="Producer"):
        self.name = name
        self.queue = None
        self.event = None
        self.thread = None

    def __del__(self):
        logging.debug(f"{self.name} terminate")

    def start_thread(self, queue, event):
        self.queue = queue
        self.event = event

        self.setup_thread()

        self.thread = threading.Thread(name=self.name, target=self.run)
        self.thread.start()

    def join_thread(self):
        self.thread.join()

    def run(self):
        logging.info(f"{self.name} running")

        while not self.event.is_set():

            ret, product = self.produce_in_thread()
            if not ret:
                self.event.set()
                break

            self.queue.put(product)
            self.nproduce += 1

        self.last_inthread_execution()

    # NOTE: este método que hay que sobre-escribir:
    def setup_thread(self):
        logging.debug(f"{self.name} setup thread")

    # NOTE: este método que hay que sobre-escribir:
    def produce_in_thread(self):
        u"""Método de producción."""
        logging.debug(f"{self.name} producing")

        if self.nproduce == 15:
            return False, None

        time.sleep(random.random())
        return True, self.nproduce

    # NOTE: este método que hay que sobre-escribir:
    def last_inthread_execution(self):
        logging.debug(f"{self.name} last thread execution")


class Consumer:

    def __init__(self, name="Consumer"):
        self.name = name
        self.event = None
        self.queue = None
        self.thread = None
        self.nconsume = 0

    def __del__(self):
        logging.debug(f"{self.name} terminate")

    def start_thread(self, queue, event):
        self.queue = queue
        self.event = event

        self.setup_thread()

        self.thread = threading.Thread(name=self.name, target=self.run)
        self.thread.start()

    def join_thread(self):
        self.thread.join()

    def run(self):
        logging.info(f"{self.name} running")
        while (not self.event.is_set()) or (not self.queue.empty()):

            self.consume_in_thread(self.queue.get())
            self.queue.task_done()
            self.nconsume += 1

        self.last_inthread_execution()

    # NOTE: este método que hay que sobre-escribir:
    def setup_thread(self):
        logging.debug(f"{self.name} setup thread")

    # NOTE: este método que hay que sobre-escribir:
    def consume_in_thread(self, value):
        u"""Método de consumo."""
        logging.debug(f"{self.name} consuming")
        time.sleep(random.random())

    # NOTE: este método que hay que sobre-escribir:
    def last_inthread_execution(self):
        logging.debug(f"{self.name} last thread execution")
