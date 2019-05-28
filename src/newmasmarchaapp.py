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

import logging
# import os
# from time import sleep
# from queue import Queue
# from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
# from kivy.core.window import Window
#
from kivy.uix.gridlayout import GridLayout
from .settings import app_config  #, new_session, CONFIG_PATH

# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.popup import Popup

# from .video import Video, Pics
# from .videoexplorer import Explorer

# from .kinematics import Kinematics
# from .representation import WalkPlot, SpatioTemporal, AnglePlot, ROM


def printConfig(dt):
    for key in app_config:
        for value in app_config[key]:
            print(value, app_config[key][value])


class NewMasMarchaApp(App):

    def schedullePrintConfig(self):
        Clock.schedule_interval(printConfig, 5)

    def build(self):
        u"""Construye la interfaz gráfica."""
        self.config = app_config
        main = MainFrame()
        main.buildConfigOptions()
        self.schedullePrintConfig()
        return main


class MainFrame(GridLayout):
    rows = 5  # DELETE
    pass

    def buildConfigOptions(self):
        u"""Construye los widgets de configuración de sección."""
        widget = ConfigOption1("Dilatación", "explorer", "dilate").build(app_config)
        self.add_widget(widget)
        widget = ConfigOption1("FiltradoXduración", "kinematics", "filter_by_duration").build(app_config)
        self.add_widget(widget)
        widget = ConfigOption2("NumMarcadores", "schema", "n").build(app_config, 5, 14, 1)
        self.add_widget(widget)
        widget = ConfigOption3("Logitud Derecha", "kinematics", "leftlength").build(app_config, 0.15, 0.4, 0.01)
        self.add_widget(widget)
        widget = ConfigOption4("1er Ciclador", "kinematics", "cyclemarker.1").build(app_config)
        self.add_widget(widget)


class ConfigWidget(GridLayout):
    u"""Clase base de widgets de configuración de variables de usuario."""

    def __init__(self, label, section, variable, *args, **kwargs):
        super().__init__()
        self.section = section
        self.variable = variable
        self.ids.label.text = label

    def build(self, config):
        return NotImplemented


class ConfigOption1(ConfigWidget):
    u"""Widget para ajustes de configuración de tipo Boleano."""
    current_value = BooleanProperty(False)

    def build(self, config):
        self.config = config
        self.current_value = config.getboolean(self.section, self.variable)
        return self

    def change_option(self):
        self.current_value = not self.current_value

    def on_current_value(self, instance, value):
        self.config.set(self.section, self.variable, str(value))


class ConfigOption2(ConfigWidget):
    u"""Widget para ajustes de configuración Numérico de tipo entero."""
    current_value = NumericProperty(0)

    def build(self, config, min, max, dt):
        self.config = config
        self.interval = dt
        self.minvalue = min
        self.maxvalue = max
        self.current_value = config.getint(self.section, self.variable)
        return self

    def change_option(self):
        try:
            self.current_value = int(self.ids.showvalue.text)
        except ValueError as error:
            logging.error("Opción no válida [error]: %s" % error)
            self.current_value = self.minvalue

    def up_change_option(self):
        self.current_value += self.interval

    def down_change_option(self):
        self.current_value -= self.interval

    def validate(self, value):
        if float(value) < self.minvalue:
            self.up_change_option()
        elif float(value) > self.maxvalue:
            self.down_change_option()

    def on_current_value(self, instance, value):
        self.validate(value)
        self.config.set(self.section, self.variable, str(value))
        self.ids.showvalue.text = "{:.2f}".format(self.current_value)


class ConfigOption3(ConfigOption2):
    u"""Widget para ajustes de configuración Numérico de tipo flotante."""

    def build(self, config, min, max, dt):
        self.config = config
        self.interval = dt
        self.minvalue = min
        self.maxvalue = max
        self.current_value = config.getfloat(self.section, self.variable)
        return self

    def change_option(self):
        try:
            self.current_value = float(self.ids.showvalue.text)
        except ValueError as error:
            logging.error("Opción no válida [error]: %s" % error)
            self.current_value = self.minvalue


class ConfigOption4(ConfigWidget):
    u"""Widget para ajustes de configuración de tipo opciones establecidas."""
    current_value = StringProperty("")

    def build(self, config):
        self.config = config
        self.ids.optionsvalue.values = self.getVariables()
        return self

    def getVariables(self):
        values = []
        for variable in self.config[self.section]:
            if variable.split('.')[0] == self.variable.split('.')[0]:
                values.append(self.config[self.section][variable])
        return values

    def change_option(self):
        self.current_value = self.ids.optionsvalue.text

    def on_current_value(self, instance, value):
        self.config.set(self.section, self.variable, str(value))




# class Control(GridLayout):
#     pass
#
#
# class LoadDialog(FloatLayout):
#     load = ObjectProperty(None)
#     source = StringProperty(None)
#
#
# class VidControl(GridLayout):
#     sourcefile = None
#
#     def dismiss_popup(self):
#         self._popup.dismiss()
#
#     def show_load(self):
#         u"""Popup para buscar la ruta del video."""
#         sourcedir = self.config.get('paths', 'sourcedir')
#         self._content = LoadDialog(load=self.load, source=sourcedir)
#         self._popup = Popup(title='Seleccionar Video', content=self._content)
#         self._popup.open()
#
#     def load(self, path, filename):
#         u"""Establece la ruta del archivo fuente de video en el sistema."""
#         if not self._content.ids['filechooser'].selection:
#             return
#         self.ids.sourcefile.text = os.path.join(path, filename[0])
#         self.dismiss_popup()
#
#     def load_video(self):
#         self.video = Video(self.config)
#         value = self.ids.sourcefile.text
#         if os.path.isfile(value):
#             self.new_session(value)  # NOTE: esta implementación hace innecesaria "sourcefile"
#             self.sourcefile = value
#             self.video.open(value)
#             self.progressbar.max = self.video.videosize
#
#     def progress(self, pqueue):
#         while True:
#             value = pqueue.get()
#             if value is -1:
#                 break
#             self.progressbar.value = value
#             pqueue.task_done()
#             sleep(.00001)
#         self.process_walks()
#         self.walks.walks.clear()
#         self.walks.walks.update({str(w): w for w in self.explorer.walks})
#         self.progressbar.value = 0
#
#     def process_walks(self):
#         for walk in self.explorer.walks:
#             walk.find_markers()
#
#     def find_walks(self):
#         u"""Lanza el proceso de procesamiento del video."""
#         self.explorer.findWalks(self.video)
#         self.process_walks()
#         self.walks.walks.update({str(w): w for w in self.explorer.walks})
#         # if self.sourcefile is None:
#         #     return
#         # self.progressbar.value = 10
#         # q = Queue()
#         # t1 = Thread(target=self.explorer.findWalks, args=(q,), daemon=True)
#         # t2 = Thread(target=self.progress, args=(q,), daemon=True)
#         # t1.start()
#         # t2.start()
#
#     def preview(self):
#         if self.sourcefile is None:
#             return
#         self.explorer.preview(self.config.getfloat('video', 'delay'))
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
