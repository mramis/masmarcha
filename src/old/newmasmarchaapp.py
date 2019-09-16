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
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout

from .core.main import Core
from .core.settings import config, SCHEMA as schema
from .uix.videoframe import VideoFrame
from .uix.walksframe import WalksFrame
from .uix.displayframe import DisplayFrame


Window.size = (1600, 700)


class NewMasMarchaApp(App):
    core = Core(config, schema)

    def build(self):
        u"""Construye la interfaz gráfica."""
        root = BoxLayout()

        self.player = DisplayFrame()
        self.worksection = WorkSection()
        self.worksection.widgets = [VideoFrame(), WalksFrame()]

        root.add_widget(self.worksection)
        root.add_widget(self.player)
        return root


class WorkSection(BoxLayout):
    orientation = "vertical"
    widgets = ListProperty([])
    spacing = 50

    def on_widgets(self, instance, widgets):
        u"""Agrega los widgets de secciones de trabajo."""
        for w in widgets:
            self.add_widget(w)


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
