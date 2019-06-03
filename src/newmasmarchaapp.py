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

from kivy.app import App

# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.popup import Popup

# from .kinematics import Kinematics
# from .representation import WalkPlot, SpatioTemporal, AnglePlot, ROM



class NewMasMarchaApp(App):

    def build(self):
        u"""Construye la interfaz gráfica."""
        self.config = app_config
        video = VideoFrame()
        return video

####### videoIwdgetFile.py ################
import queue
import time
import threading

from kivy.clock import mainthread
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ObjectProperty

from .video import Video, explore_video
from .settings import app_config
from .uix.configwidgets import BoolOption, IntegerOption, FloatOption


class VideoFrame(GridLayout):
    u"""Frame de control de video."""
    current_video = StringProperty(None, allownone=True)
    positions = []
    walks = queue.Queue()

    def show_load(self):
        u"""Popup para buscar la ruta del video."""
        sourcedir = app_config.get("paths", "sourcedir")
        self._content = LoadDialog(load=self.load, source=sourcedir)
        self._popup = Popup(title='Seleccionar Video', content=self._content)
        self._popup.open()

    def dismiss_popup(self):
        u"""Destruye el popup de archivos."""
        self._popup.dismiss()

    def load(self, filepath):
        u"""Establece la ruta del archivo fuente de video en el sistema."""
        value = filepath.pop(0) if filepath != [] else None
        if value is not None:
            ext = value.split('.')[-1]
            if ext in app_config.get("video", "extensions").split(','):
                self.current_video = value
                self.dismiss_popup()

    def load_video(self):
        """Carga el archivo de video."""
        self.video = Video(app_config)
        self.video.open(self.current_video)
        self.ids.endframe.current_value = self.video.size
        self.ids.startframe.current_value = 0

    def on_current_video(self, instance, value):
        u"""Agrega la ruta a la lista de rutas."""
        self.ids.show_file.text = value
        self.load_video()

    def show_video(self):
        u"""Muestra el archivo de video seleccionado."""
        if self.current_video is None:
            self.show_load()
            return
        self.video.view("preview")

    def explore_video(self, queue):
        u"""Realiza la exploración del video en busca de caminatas."""
        if self.current_video is None:
            self.show_load()
            return
        for walk, framepos in explore_video(self.video):
            self.upload_progress(framepos)
            queue.put(walk)
        self.reset_progress()

    def run_explorer_thread(self):
        u"""Inicia la exploración en otro hilo."""
        # NOTE: Por ahora el contenedor walks pertenece al widget de video.
        threading.Thread(target=self.explore_video, args=(self.walks,)).start()

    @mainthread
    def upload_progress(self, progress):
        u"""Actualiza el progreso de exploración de video."""
        value = (progress / self.video.size) * 100
        self.ids.progressbar.value = value
        self.ids.progresstext.text = "Progreso {:.2f}%".format(value)

    @mainthread
    def reset_progress(self):
        self.ids.progressbar.value = 0
        self.ids.progresstext.text = "Progreso"


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    source = StringProperty(None)



    # def load_video(self):
    #     self.video = Video(self.config)
    #     value = self.ids.sourcefile.text
    #     if os.path.isfile(value):
    #         self.new_session(value)  # NOTE: esta implementación hace innecesaria "sourcefile"
    #         self.sourcefile = value
    #         self.video.open(value)
    #         self.progressbar.max = self.video.videosize
    #
    # def progress(self, pqueue):
    #     while True:
    #         value = pqueue.get()
    #         if value is -1:
    #             break
    #         self.progressbar.value = value
    #         pqueue.task_done()
    #         sleep(.00001)
    #     self.process_walks()
    #     self.walks.walks.clear()
    #     self.walks.walks.update({str(w): w for w in self.explorer.walks})
    #     self.progressbar.value = 0
    #
    # def process_walks(self):
    #     for walk in self.explorer.walks:
    #         walk.find_markers()
    #
    # def find_walks(self):
    #     u"""Lanza el proceso de procesamiento del video."""
    #     self.explorer.findWalks(self.video)
    #     self.process_walks()
    #     self.walks.walks.update({str(w): w for w in self.explorer.walks})
    #     # if self.sourcefile is None:
    #     #     return
    #     # self.progressbar.value = 10
    #     # q = Queue()
    #     # t1 = Thread(target=self.explorer.findWalks, args=(q,), daemon=True)
    #     # t2 = Thread(target=self.progress, args=(q,), daemon=True)
    #     # t1.start()
    #     # t2.start()
    #



#
#
# class WalksControl(GridLayout):
#     walks = DictProperty({})
#
#     def on_walks(self, instace, value):
#         self.current = None
#         self.ids.choice.text = self.ids.choice.default
#         self.ids.choice.values = sorted(self.walks.keys())
#
#     def choice(self, wid):
#         self.current = self.walks[wid]
#
#     def walkview(self):
#         if self.current is None:
#             return
#         delay = self.config.getfloat('video', 'delay')
#         self.explorer.walkview(self.current, delay)
#
#
# class PlotsControl(GridLayout):
#     cids = []
#
#     def get_params(self):
#         self.kinematics.start()
#         self.kinematics.cycle_walks(self.explorer.walks)
#         self.kinematics.build_segments()
#
#     def select(self):
#         self.cids = [s.strip() for s in self.ids.toremove.text.split(',')]
#
#     def remove(self):
#         self.kinematics.delete_cycles(self.cids)
#         self.plot()
#
#     def plot(self, getparams=False):
#         # NOTE:  TODA ESTA SECCIÓN TIENE UN MAL DISEÑO.
#         # POR AHORA TODAS LAS IMÁGENES QUE SE CREAN VAN A SALR DE ACÁ
#         # PERO ES NECESARIO REDISEÑAR EL PROCESO.
#         if not self.explorer.source:
#             return
#         import numpy as np  # NOTE: quitar cuando se formalice la tabla rom
#         destpath = self.config.get('current', 'session')
#
#         if getparams:
#             self.get_params()
#
#         # NOTE: resultados del ciclado.
#         walks = WalkPlot(self.config)
#         # NOTE: por ahora se obtienen del cycler
#         walks.plot(self.kinematics.cycler, self.config.get('current', 'walks'))
#
#
#         # Pics de los cyclos.
#         pics = Pics(self.config)
#         pics.open(self.explorer.source)
#         pics.make_pics(self.kinematics.cycler.cyclessv, self.explorer.walks)
#
#
#         labels, direction, stp, hip, knee, ankle = self.kinematics.to_plot()
#         # Por ahora no se están aceptando en la tabla los datos de tiempos de
#         # fase
#         stp = stp[:, [1, 4, 5, 6, 7, 8]]
#
#         # parámetros espacio temporales
#         leftstp = stp[direction == 0].mean(axis=0).round(1)
#         rightstp = stp[direction == 1].mean(axis=0).round(1)
#         tablestp = SpatioTemporal(self.config, "Parámetros espacio-temporales")
#         tablestp.build(params=np.array((leftstp, rightstp)).transpose())
#         tablestp.save(destpath)
#         # cinemática ángulos
#         angles = AnglePlot('Cinematica', config=self.config)
#         angles.add_joint('cadera', direction, labels, hip, stp[:, 1])
#         angles.add_joint('rodilla', direction, labels, knee, stp[:, 1])
#         angles.add_joint('tobillo', direction, labels, ankle, stp[:, 1])
#         angles.plot(putlegends=True)
#         angles.save(destpath)
#
#         # cadera
#         h = AnglePlot('Cadera', config=self.config)
#         h.add_joint('hip', direction, labels, hip, stp[:, 1])
#         h.plot(summary=True)
#         h.save(destpath)
#
#         # rodilla
#         k = AnglePlot('Rodilla', config=self.config)
#         k.add_joint('knee', direction, labels, knee, stp[:, 1])
#         k.plot(summary=True)
#         k.save(destpath)
#
#         # tobillo
#         a = AnglePlot('Tobillo', config=self.config)
#         a.add_joint('ankle', direction, labels, ankle, stp[:, 1])
#         a.plot(summary=True)
#         a.save(destpath)
#
#         # ROM
#         maxlh = np.max(np.nanmean(hip[direction == 0], axis=0))
#         minlh = np.min(np.nanmean(hip[direction == 0], axis=0))
#         maxrh = np.max(np.nanmean(hip[direction == 1], axis=0))
#         minrh = np.min(np.nanmean(hip[direction == 1], axis=0))
#
#         maxlk = np.max(np.nanmean(knee[direction == 0], axis=0))
#         minlk = np.min(np.nanmean(knee[direction == 0], axis=0))
#         maxrk = np.max(np.nanmean(knee[direction == 1], axis=0))
#         minrk = np.min(np.nanmean(knee[direction == 1], axis=0))
#
#         maxla = np.max(np.nanmean(ankle[direction == 0], axis=0))
#         minla = np.min(np.nanmean(ankle[direction == 0], axis=0))
#         maxra = np.max(np.nanmean(ankle[direction == 1], axis=0))
#         minra = np.min(np.nanmean(ankle[direction == 1], axis=0))
#
#         rom = np.array((
#             ((minlh.round(1), maxlh.round(1), minrh.round(1), maxrh.round(1)),
#              (minlk.round(1), maxlk.round(1), minrk.round(1), maxrk.round(1)),
#              (minla.round(1), maxla.round(1), minra.round(1), maxra.round(1))))
#         )
#         romtable = ROM(self.config, "Rango de movimiento")
#         romtable.build(rom)
#         romtable.save(destpath)
