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

from .settings import app_config
from .uix.videoframe import VideoFrame


class NewMasMarchaApp(App):
    data_container = {"walks": ["Todas"] + [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14]}  # remove

    def build(self):
        u"""Construye la interfaz gráfica."""
        self.config = app_config
        # videoframe = VideoFrame()
        # return videoframe
        walksframe = WalksFrame()
        return walksframe

    @property
    def walks_container(self):
        return self.data_container["walks"]



####### WalksFrame >>>>>>>>>>
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout


class WalksFrame(GridLayout):
    current_walk_index = NumericProperty(None)
    process_all = True

    def show_selector(self):
        u"""Popup para seleccionar la caminata."""
        self._popup = Popup(title='Seleccionar Caminata',
                            size_hint=(None, None),
                            content=SelectionDialog(select=self.select),
                            size=(250, 400))
        self._popup.open()

    def dismiss_popup(self):
        u"""Destruye el popup de selección de caminata."""
        self._popup.dismiss()

    def select(self, button):
        u"""Establece el índice(posición) en lista de la caminata."""
        self.current_walk_index = button.wid
        self.dismiss_popup()

    def select_forward(self):
        u"""Incrementa en uno el valor del índice de la caminata."""
        maxindex = len(self.walks) - 1
        if self.current_walk_index < maxindex:
            self.current_walk_index += 1

    def select_backward(self):
        u"""Decrementa en uno el valor del índice de la caminata."""
        if self.current_walk_index == 0:
            return
        else:
            self.current_walk_index -= 1

    def on_current_walk_index(self, instance, value):
        if self.walks[value] == "Todas":
            label = "Todas"
            self.process_all = True
        else:
            label = "CAMINATA %s - 234 FRAMES" % str(self.walks[value])
            self.process_all = False
        self.ids.show_walk.text = label


class SelectionDialog(FloatLayout):
    walks = ListProperty(None)
    select = ObjectProperty(None)

    def on_walks(self, instance, contentlist):
        for e, element in enumerate(contentlist):
            btn = WalkButton(text=str(element), on_release=self.select)
            btn.wid = e
            self.ids.stack.add_widget(btn)


class WalkButton(Button):
    pass

###### END <<<<<<<<<<<<<<<<<<



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