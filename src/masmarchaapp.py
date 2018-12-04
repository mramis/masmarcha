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
import sys
from json import load
from configparser import ConfigParser
from collections import defaultdict
from subprocess import call

import numpy as np
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.filechooser import FileChooserListView

from video import Explorer
import kinematics
import representation2 as repr

# TODO:
# [] Mejorar la declaración del esquema que se carga en tres funciones de un
# mismo objeto.
# [] Revisar el código de video y kinematics para hacer más prolijo el codigo
# acá.


class MasMarchaApp(App):

    def __init__(self, configpath):
        super().__init__()
        self.configpath = configpath

    def build_config(self, config):
        config.read(self.configpath)

    def build(self):
        u"""Construye la interfaz gráfica."""
        return MainFrame()


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    source = StringProperty(None)


class MainFrame(GridLayout):

    def __init__(self):
        super().__init__()
        self.schema = load(open(self.config.get('paths', 'schema')))
        self.sac = np.load(self.config.get('paths', 'normal'))

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
        self.sourcefile = os.path.join(path, filename[0])
        self.ids['sourcefile'].text = self.sourcefile
        self.dismiss_popup()

    def video_preview(self):
        if self.sourcefile:
            self.explorer = Explorer(self.sourcefile, self.schema, self.config)
            self.explorer.preview(self.config.getfloat('explorer', 'delay'))

    def video_explorer(self):
        """Explorador de video."""
        self.ids['outcomes'].clear()
        if self.sourcefile:
            explorer = Explorer(self.sourcefile, self.schema, self.config)
            explorer.find_walks()
            self.group_cycles(explorer.walks)

    def group_cycles(self, walks):
        """Calcula los ciclos de las caminatas y las agrupa."""
        threshold = self.config.getfloat('cycles', 'threshold')
        outcomes = (self.ids['outcomes'].leftside,
                    self.ids['outcomes'].rightside)
        # NOTE: HARDCORE: FPS; LEGDISTANCE
        cyclesgen = kinematics.calculate(
            walks, self.schema, threshold, 60, (0, 0))
        for (codename, direction, stp, ang) in cyclesgen:
            cycle = Cycle(codename)
            cycle.spatiotemporal = stp
            cycle.angles = ang
            outcomes[direction].append(cycle)


class Outcomes(GridLayout):
    leftside = ListProperty()
    rightside = ListProperty()

    def on_leftside(self, instance, listvalues):
        self.ids['leftside'].add_widget(listvalues[-1])

    def on_rightside(self, instance, listvalues):
        self.ids['rightside'].add_widget(listvalues[-1])

    def clear(self):
        self.leftside.clear()
        self.ids['leftside'].clear_widgets()
        self.rightside.clear()
        self.ids['rightside'].clear_widgets()

    def plot(self, source, sac):
        # Parametros espaciotemporales.
        stp = {'left': [], 'right': []}
        # Curvas de angulos.
        angles = {
            'left': {'hip': [], 'knee': [], 'ankle': [], 'phase': []},
            'right':{'hip': [], 'knee': [], 'ankle': [], 'phase': []}}
        legends = {'left': [], 'right': []}

        for cycle in self.leftside:
            if cycle.is_active():
                stp['left'].append(cycle.spatiotemporal)
                angles['left']['hip'].append(cycle.angles[0])
                angles['left']['knee'].append(cycle.angles[1])
                angles['left']['ankle'].append(cycle.angles[2])
                angles['left']['phase'].append(cycle.spatiotemporal[1])
                legends['left'].append(cycle.id)

        for cycle in self.rightside:
            if cycle.is_active():
                stp['right'].append(cycle.spatiotemporal)
                angles['right']['hip'].append(cycle.angles[0])
                angles['right']['knee'].append(cycle.angles[1])
                angles['right']['ankle'].append(cycle.angles[2])
                angles['right']['phase'].append(cycle.spatiotemporal[1])
                legends['right'].append(cycle.id)

        if self.leftside or self.rightside:
            # Parámetros de referencia
            norm = sac.get('mean_angles')
            std = sac.get('std_angles')
            normet = sac.get('mean_spacetemporal')
            stdet = sac.get('std_spacetemporal')
            src = os.path.basename(source).split('.')[0]
            repr.plot(src, stp, angles, legends, norm, std, normet, stdet)

        if sys.platform == 'linux':
            call(['eog', '10-Casa-Leticia-Cinemática-Derecho.png'])


class Cycle(GridLayout):

    def __init__(self, cycle_id):
        super().__init__()
        self.id = cycle_id
        self.ids['label'].text = cycle_id

    def is_active(self):
        return self.ids['check'].active


# class ConfigVar(ttk.Frame):
#
#     def __init__(self, parent, labelname, key):
#         super().__init__(parent)
#         self.config = parent.config
#         self.section = parent.section
#         self.key = key
#
#         self.label = ttk.Label(self, text=labelname)
#         self.var = tk.StringVar(value=self.config.get(self.section, key))
#         self.box = tk.Spinbox(self, textvariable=self.var, command=self.update)
#         self.box.bind('<Return>', self.update_on_return)
#         self.build()
#
#     def set_numerical(self, **kwargs):
#         if 'float' in kwargs.keys():
#             kwargs['format'] = '%.1f'
#             kwargs['increment'] = 0.1
#             kwargs.pop('float')
#             self.kind = 'float'
#         else:
#             self.kind = 'int'
#         self.box.configure(**kwargs)
#
#     def set_categorical(self, *args):
#         self.box.configure(values=args)
#         self.kind = 'str'
#
#     def update(self):
#         self.config.set(self.section, self.key, self.var.get())
#         with open(self.config.get('paths', 'config'), 'w') as fh:
#             self.config.write(fh)
#
#     def update_on_return(self, event):
#         if self.kind == 'str':
#             self.var.set(value=self.box['values'].split()[0])
#             self.update()
#             self.focus()
#             self.bell()
#             return
#
#         try:
#             val = float(self.var.get())
#         except:
#             val = -1
#         fr = self.box['from']
#         to = self.box['to']
#         if val >= fr and val <= to:
#             self.update()
#             self.focus()
#         else:
#             df1 = abs(fr - val)
#             df2 = abs(to - val)
#             value = fr if df1 < df2 else to
#             self.var.set(value=(value if self.kind == 'float' else int(value)))
#             self.update()
#             self.focus()
#             self.bell()
#
#     def build(self):
#         self.label.pack()
#         self.box.pack()
#         self.pack(ipady=10, ipadx=10)
#
#
# class ConfigTab(ttk.Notebook):
#
#     def __init__(self, root, config):
#         super().__init__(root)
#         self.config = config
#
#     def build(self):
#         # Section: explorerconfig
#         explorer = ttk.Frame(self)
#         explorer.config = self.config
#         explorer.section = 'explorer'
#         self.add(explorer, text='Explorardor')
#
#         dilatevar = ConfigVar(explorer, 'Dilatación', 'dilate')
#         dilatevar.set_numerical(from_=0, to=10)
#         thresholdvar = ConfigVar(explorer, 'Umbral', 'threshold')
#         thresholdvar.set_numerical(from_=230, to=255)
#         extrapixelvar = ConfigVar(explorer, 'Extra-Pixel', 'extrapixel')
#         extrapixelvar.set_numerical(from_=10, to=50)
#         roimethodvar = ConfigVar(explorer, 'Método ROI', 'roimethod')
#         roimethodvar.set_categorical('Banda', 'Cuadro')
#
#         # # Section: displayconfig
#         display = ttk.Frame(self)
#         display.config = self.config
#         display.section = 'display'
#         self.add(display, text='Visualizador')
#
#         framewidthvar = ConfigVar(display, 'Ancho display', 'framewidth')
#         framewidthvar.set_numerical(from_=200, to=1090)
#         frameheightvar = ConfigVar(display, 'Alto display', 'frameheight')
#         frameheightvar.set_numerical(from_=200, to=1090)
#
#         # # Section: cameraconfig
#         camera = ttk.Frame(self)
#         camera.config = self.config
#         camera.section = 'camera'
#         self.add(camera, text='Cámara')
#         fpscorrectvar = ConfigVar(camera, 'Corrección de FPS', 'fpscorrection')
#         fpscorrectvar.set_numerical(from_=0, to=10)
#
#         # # Section: cyclesconfig
#         cycles = ttk.Frame(self)
#         cycles.config = self.config
#         cycles.section = 'cycles'
#         self.add(cycles, text='Ciclos')
#
#         phasethresholdvar = ConfigVar(cycles, 'Umbral de fase', 'threshold')
#         phasethresholdvar.set_numerical(from_=0.1, to=10, float=True)
#         cyclemarker1var = ConfigVar(cycles, '1er marcador', 'cyclemarker1')
#         cyclemarker1var.set_categorical('M5', 'M6')
#         cyclemarker2var = ConfigVar(cycles, '2do marcador', 'cyclemarker2')
#         cyclemarker2var.set_categorical('M5', 'M6')
#
#         # # Section: plotsconfig
#         plots = ttk.Frame(self)
#         plots.config = self.config
#         plots.section = 'plots'
#         self.add(plots, text='Gráficos')
#
#         aspectvar1 = ConfigVar(plots, 'Aspecto gráficos individuales',
#                                'aspect1')
#         aspectvar1.set_numerical(from_=0.1, to=1.0, float=True)
#
#         aspectvar2 = ConfigVar(plots, 'Aspecto gráficos conjuntos', 'aspect2')
#         aspectvar2.set_numerical(from_=0.1, to=1.0, float=True)
#
#         dpivar = ConfigVar(plots, 'Densidad de puntos', 'dpi')
#         dpivar.set_numerical(from_=50, to=500)
#
#         self.grid()
