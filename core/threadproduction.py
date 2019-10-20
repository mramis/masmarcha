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

import queue
import logging
import threading


class Producer:
    u"""Hilo productor genérico para correr en conjunto con al menos un
    consumidor.

    Debe sobeescribirse el método Producer.produce en la implementación.
    """
    resource_avaible = True
    resource = None
    nproduce = 0

    def __init__(self, pqueue, pevent, name="Producer"):
        self.name = f"\u001b[37;1m{name}\u001b[0m"
        self.pqueue = pqueue
        self.pevent = pevent
        self.thread = None

    def __del__(self):
        logging.debug("[terminate]")

    def start(self):
        self.thread = threading.Thread(name=self.name, target=self.run)
        self.thread.start()

    def join(self):
        self.thread.join()

    def run(self):
        logging.info("running")
        while self.resource_avaible and not self.pevent.is_set():

            self.produce()
            logging.debug(f"\u001b[37mproducing\u001b[0m {self.nproduce}")

            self.pqueue.put(self.resource)
            self.nproduce += 1

        self.pevent.set()

    # NOTE: este es el método que hay que sobre-escribir:
    def produce(self):
        u"""Método de producción."""
        self.resource = self.nproduce
        if self.nproduce == 50:
            self.resource_avaible = False


class Consumer:

    def __init__(self, cqueue, cevent, name="Consumer"):
        self.name = f"\u001b[33;1m{name}\u001b[0m"
        self.cevent = cevent
        self.cqueue = cqueue
        self.thread = None
        self.nconsume = 0
        self.intermediate = False

    def __del__(self):
        logging.debug("[terminate]")

    def becomeIntermediary(self, pqueue, pevent, name="Intermediary"):
        self.name = f"\u001b[33;1m{name}\u001b[0m"
        self.pqueue = pqueue
        self.pevent = pevent
        self.intermediate = True

    def start(self):
        self.thread = threading.Thread(name=self.name, target=self.run)
        self.thread.start()

    def join(self):
        self.thread.join()

    def run(self):
        logging.info("running")
        while (not self.cevent.is_set()) or (not self.cqueue.empty()):

            product = self.consume(self.cqueue.get())
            logging.debug(f"\u001b[33mconsuming\u001b[0m {self.nconsume}")

            if self.intermediate:
                self.pqueue.put(product)
            self.nconsume += 1

        if self.intermediate:
            self.pevent.set()

    # NOTE: este es el método que hay que sobre-escribir:
    def consume(self, value):
        u"""Método de consumo. Devuelve valor si es intermediario."""
        return value


if __name__ == '__main__':
    import time

    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(levelname)-s] %(threadName)-20s: %(message)s'
    )
    t1 = time.perf_counter()

    q1 = queue.Queue(maxsize=1)
    e1 = threading.Event()

    q2 = queue.Queue(maxsize=1)
    e2 = threading.Event()

    q3 = queue.Queue(maxsize=1)
    e3 = threading.Event()

    producer = Producer(q1, e1)

    consumer1 = Consumer(q1, e1)
    consumer2 = Consumer(q2, e2)
    consumer3 = Consumer(q3, e3)
    consumer1.becomeIntermediary(q2, e2, name="inter1")
    consumer2.becomeIntermediary(q3, e3, name="inter2")

    producer.start()
    consumer1.start()
    consumer2.start()
    consumer3.start()

    producer.join()
    consumer1.join()
    consumer2.join()
    consumer3.join()

    t2 = time.perf_counter()

    print(f"Proceso con dos intermediario finalizado en {t2-t1} segundos")
