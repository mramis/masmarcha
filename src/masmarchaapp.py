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

import os
from time import sleep
from queue import Queue
from threading import Thread

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, DictProperty
from kivy.core.window import Window

from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup

from .video import Explorer
from .settings import app_config, new_session
from .kinematics import Kinematics
from .representation import SpatioTemporal, AnglePlot, ROM


Window.size = (1200, 800)


class MasMarchaApp(App):

    def build(self):
        u"""Construye la interfaz gráfica."""
        self.config = app_config
        self.explorer = Explorer(self.config)
        self.kinematics = Kinematics(self.config)
        return MainFrame()


class MainFrame(GridLayout):
    pass


class Session(GridLayout):

    def session_data_collect(self):
        for i in self.ids.items():
            print(i)


class Control(GridLayout):
    pass


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    source = StringProperty(None)


class VidControl(GridLayout):
    sourcefile = None

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        u"""Popup para buscar la ruta del video."""
        sourcedir = self.config.get('paths', 'sourcedir')
        self._content = LoadDialog(load=self.load, source=sourcedir)
        self._popup = Popup(title='Seleccionar Video', content=self._content)
        self._popup.open()

    def load(self, path, filename):
        u"""Establece la ruta del archivo fuente de video en el sistema."""
        if not self._content.ids['filechooser'].selection:
            return
        self.ids.sourcefile.text = os.path.join(path, filename[0])
        self.dismiss_popup()

    def load_video(self):
        value = self.ids.sourcefile.text
        if os.path.isfile(value):
            self.sourcefile = value
            self.explorer.open_file(value)
            self.progressbar.max = self.explorer.nframes

    def progress(self, pqueue):
        while True:
            value = pqueue.get()
            if value is -1:
                break
            self.progressbar.value = value
            pqueue.task_done()
            sleep(.00001)
        self.process_walks()
        self.walks.walks.clear()
        self.walks.walks.update({str(w): w for w in self.explorer.walks})
        self.progressbar.value = 0

    def process_walks(self):
        for walk in self.explorer.walks:
            walk.find_markers()

    def find_walks(self):
        u"""Lanza el proceso de procesamiento del video."""
        if self.sourcefile is None:
            return
        self.progressbar.value = 10
        q = Queue()
        t1 = Thread(target=self.explorer.find_walks, args=(q,), daemon=True)
        t2 = Thread(target=self.progress, args=(q,), daemon=True)
        t1.start()
        t2.start()

    def preview(self):
        if self.sourcefile is None:
            return
        self.explorer.preview(self.config.getfloat('video', 'delay'))


class WalksControl(GridLayout):
    walks = DictProperty({})

    def on_walks(self, instace, value):
        self.current = None
        self.ids.choice.text = self.ids.choice.default
        self.ids.choice.values = sorted(self.walks.keys())

    def choice(self, wid):
        self.current = self.walks[wid]

    def walkview(self):
        if self.current is None:
            return
        delay = self.config.getfloat('video', 'delay')
        self.explorer.walkview(self.current, delay)


class PlotsControl(GridLayout):
    cids = []

    def get_params(self):
        self.kinematics.start()
        self.kinematics.cycle_walks(self.explorer.walks)
        self.kinematics.build_segments()

    def select(self):
        self.cids = [s.strip() for s in self.ids.toremove.text.split(',')]

    def remove(self):
        self.kinematics.delete_cycles(self.cids)
        self.plot()

    def plot(self, getparams=False):
        if not self.explorer.source:
            return
        import numpy as np  # NOTE: quitar cuando se formalice la tabla rom
        destpath = new_session(self.explorer.source)

        if getparams:
            self.get_params()
        labels, direction, stp, hip, knee, ankle = self.kinematics.to_plot()
        # Por ahora no se están aceptando en la tabla los datos de tiempos de
        # fase
        stp = stp[:, [1, 4, 5, 6, 7, 8]]

        # parámetros espacio temporales
        leftstp = stp[direction == 0].mean(axis=0).round(1)
        rightstp = stp[direction == 1].mean(axis=0).round(1)
        tablestp = SpatioTemporal(self.config, "Parámetros espacio-temporales")
        tablestp.build(params=np.array((leftstp, rightstp)).transpose())
        tablestp.save(destpath)
        # cinemática ángulos
        angles = AnglePlot('Cinematica', config=self.config)
        angles.add_joint('cadera', direction, labels, hip, stp[:, 1])
        angles.add_joint('rodilla', direction, labels, knee, stp[:, 1])
        angles.add_joint('tobillo', direction, labels, ankle, stp[:, 1])
        angles.plot(putlegends=True)
        angles.save(destpath)

        # cadera
        h = AnglePlot('Cadera', config=self.config)
        h.add_joint('hip', direction, labels, hip, stp[:, 1])
        h.plot(summary=True)
        h.save(destpath)

        # rodilla
        k = AnglePlot('Rodilla', config=self.config)
        k.add_joint('knee', direction, labels, knee, stp[:, 1])
        k.plot(summary=True)
        k.save(destpath)

        # tobillo
        a = AnglePlot('Tobillo', config=self.config)
        a.add_joint('ankle', direction, labels, ankle, stp[:, 1])
        a.plot(summary=True)
        a.save(destpath)

        # ROM
        maxlh, minlh = np.max(hip[direction == 0].mean(axis=0)), np.min(hip[direction == 0].mean(axis=0))
        maxrh, minrh = np.max(hip[direction == 1].mean(axis=0)), np.min(hip[direction == 1].mean(axis=0))

        maxlk, minlk = np.max(knee[direction==0].mean(axis=0)), np.min(knee[direction==0].mean(axis=0))
        maxrk, minrk = np.max(knee[direction==1].mean(axis=0)), np.min(knee[direction==1].mean(axis=0))

        maxla, minla = np.max(ankle[direction==0].mean(axis=0)), np.min(ankle[direction==0].mean(axis=0))
        maxra, minra = np.max(ankle[direction==1].mean(axis=0)), np.min(ankle[direction==1].mean(axis=0))

        rom = np.array((
                        ((minlh.round(1), maxlh.round(1), minrh.round(1), maxrh.round(1)),
                         (minlk.round(1), maxlk.round(1), minrk.round(1), maxrk.round(1)),
                         (minla.round(1), maxla.round(1), minra.round(1), maxra.round(1)))))
        romtable = ROM(self.config, "Rango de movimiento")
        romtable.build(rom)
        romtable.save(destpath)
