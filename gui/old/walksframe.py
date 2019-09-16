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

from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ObjectProperty, ListProperty


class WalksFrame(GridLayout):
    current_walk_index = NumericProperty(None)
    current_walk = ObjectProperty(None)

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
        self.current_walk_index = button.id
        self.dismiss_popup()

    def select_forward(self):
        u"""Incrementa en uno el valor del índice de la caminata."""
        if self.core.walks == [] or self.current_walk_index is None:
            return
        elif self.current_walk_index < len(self.core.walks) - 1:
            self.current_walk_index += 1

    def select_backward(self):
        u"""Decrementa en uno el valor del índice de la caminata."""
        if self.core.walks == [] or self.current_walk_index is None:
            return
        elif self.current_walk_index != 0:
            self.current_walk_index -= 1

    def on_current_walk(self, instance, walk):
        u"""Procesa la caminata y/o actualiza los valores de procesamiento."""
        mssg = "{} - {} FRAMES"
        self.core.walk = walk
        if not walk.processed_flag:
            ### SE TIENE QUE CREAR UNA FUNCIÓN QUE PUEDA INFORMAR SI SE PROCESA O NO,
            try:
                walk.process()
            except:
                return
        else:
            self.get_walk_config(walk)
        self.ids.show_walk.text = mssg.format(walk, walk.duration)
        self.ids.startframe.current_value = walk.startframe
        self.ids.endframe.current_value = walk.endframe

    def on_current_walk_index(self, instance, index):
        u"""Establece la caminata actual."""
        self.current_walk = self.core.walks[index]

    def get_walk_config(self, walk):
        u"""Muestra los valores de configuración utilizados en la caminata."""
        # Los widgets de regiones.
        self.ids.roiwidth.current_value = walk.roiwidth
        self.ids.roiheight.current_value = walk.roiheight

    def process(self):
        u"""Dispara el procesiento de la caminata con la configuración actual."""
        if self.current_walk is not None:
            self.current_walk.process()

    def play(self):
        u"""Muestra el archivo de video seleccionado."""
        if self.current_walk is not None:
            self.appplayer.play = True

    def stop(self):
        u"""Detiene la reproducción."""
        self.appplayer.play = False


class SelectionDialog(FloatLayout):
    walks = ListProperty(None)
    select = ObjectProperty(None)

    def on_walks(self, instance, collection):
        for e, walk in enumerate(collection):
            btn = WalkButton(text=str(walk), on_release=self.select, id=e)
            self.ids.stack.add_widget(btn)


class WalkButton(Button):
    id = NumericProperty(None)
