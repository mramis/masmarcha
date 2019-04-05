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
from .settings import PathManager
from .kinematics import Kinematics
from .representation import SpatioTemporal, AnglePlot, ROM


Window.size = (1200, 800)


class MasMarchaApp(App):
    pathmanager = PathManager()

    def build_config(self, config):
        config.add_section('paths')
        config.set('paths', 'app', self.pathmanager.app)
        config.set('paths', 'sourcedir', self.pathmanager.home)
        config.set('paths', 'normal_', self.pathmanager.normal)
        config.set('paths', 'normal_stp',
                   os.path.join(self.pathmanager.normal, 'stp.csv'))
        config.set('paths', 'normal_rom',
                   os.path.join(self.pathmanager.normal, 'rom.csv'))
        config.set('paths', 'normal_hip',
                   os.path.join(self.pathmanager.normal, 'hip.csv'))
        config.set('paths', 'normal_knee',
                   os.path.join(self.pathmanager.normal, 'knee.csv'))
        config.set('paths', 'normal_ankle',
                   os.path.join(self.pathmanager.normal, 'ankle.csv'))

        config.add_section('explorer')
        config.set('explorer', 'dilate', 'False')
        config.set('explorer', 'threshold', '240')

        config.add_section('walk')
        config.set('walk', 'roiwidth', '125')
        config.set('walk', 'roiheight', '35')

        config.add_section('video')
        config.set('video', 'delay', '.1')
        config.set('video', 'framewidth', '640')
        config.set('video', 'frameheight', '480')

        config.add_section('camera')
        config.set('camera', 'fps', '60')
        config.set('camera', 'fpscorrection', '1')

        config.add_section('kinematics')
        config.set('kinematics', 'stpsize', '6')
        config.set('kinematics', 'nfixed', '100')
        config.set('kinematics', 'maxcycles', '75')
        config.set('kinematics', 'leftlength', '0.28')
        config.set('kinematics', 'rightlength', '0.28')
        config.set('kinematics', 'anglessize', '100')
        config.set('kinematics', 'leftthreshold', '3.2')
        config.set('kinematics', 'rightthreshold', '3.2')
        config.set('kinematics', 'filter_by_duration', 'True')
        config.set('kinematics', 'cyclemarker1', 'M5')
        config.set('kinematics', 'cyclemarker2', 'M6')

        config.add_section('schema')
        config.set('schema', 'n', '7')
        config.set('schema', 'r', '3')
        config.set('schema', 'leg', '3,4')
        config.set('schema', 'foot', '5,6')
        config.set('schema', 'tight', '1,2')
        config.set('schema', 'markersxroi', '0,1/2,3/4,5,6')
        config.set('schema', 'order_segments', 'tight,leg,foot')
        config.set('schema', 'order_joints', 'hip,knee,ankle')

        config.add_section('plots')
        config.set('plots', 'dpi', '80')
        config.set('plots', 'textsize', '16')
        config.set('plots', 'titlesize', '23')
        config.set('plots', 'chartwidth', '8')
        config.set('plots', 'chartheight', '5')
        config.set('plots', 'tablewidth', '12')
        config.set('plots', 'tableheight', '5')
        config.set('plots', 'subtitlesize', '18')
        config.set('plots', 'standardeviation', '2')
        config.set('plots', 'cell_index_width', '0.3')
        config.set('plots', 'cell_normal_width', '0.25')

    def build(self):
        u"""Construye la interfaz gráfica."""
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
        destpath = self.pathmanager.new(self.explorer.source)

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
