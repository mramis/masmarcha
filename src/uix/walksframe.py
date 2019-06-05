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
    current_walk = None

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
        if self.walks == []:
            return
        maxindex = len(self.walks) - 1
        if self.current_walk_index < maxindex:
            self.current_walk_index += 1

    def select_backward(self):
        u"""Decrementa en uno el valor del índice de la caminata."""
        if self.walks == [] or self.current_walk_index == 0:
            return
        else:
            self.current_walk_index -= 1

# NOTE: DESDE ACA, MEJORAR LA ESTéTICA.
    def on_current_walk_index(self, instance, value):
        self.current_walk = self.walks[value]
        if self.current_walk.processed is False:
            self.current_walk.process()
        label = "%s - %d FRAMES" % (self.current_walk, self.current_walk.lastfullrow)
        self.ids.show_walk.text = label
        self.get_walkconfiguration()

    def get_walkconfiguration(self):
        if self.current_walk.processed:
            self.ids.startframe.change_option(self.current_walk.startframe)
            self.ids.endframe.change_option(self.current_walk.endframe)
            self.ids.roiwidth.change_option(self.current_walk.roiwidth)
            self.ids.roiheight.change_option(self.current_walk.roiheight)
            self.ids.verify.current_value = self.current_walk.verify

    def process(self):
        if self.current_walk is None:
            return
        self.current_walk.process()

    def view(self):
        pass


class SelectionDialog(FloatLayout):
    walks = ListProperty(None)
    select = ObjectProperty(None)

    def on_walks(self, instance, collection):
        for e, walk in enumerate(collection):
            btn = WalkButton(text=str(walk), on_release=self.select)
            btn.wid = e
            self.ids.stack.add_widget(btn)


class WalkButton(Button):
    pass
