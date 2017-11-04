#!/usr/bin/env python
# coding: utf-8

"""Docstring."""

# Copyright (C) 2017  Mariano Ramis

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


from os.path import basename

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import ListProperty


class Content(BoxLayout):
    u"""."""
    pass


class File(Button):
    u"""."""

    def __init__(self, name, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.id = name
        self.text = basename(name)

    def autoremove(self):
        u"""."""
        self.parent.all_paths.remove(self.id)
        self.parent.remove_widget(self)


class PathsViewer(GridLayout):
    u"""."""
    paths = ListProperty([])
    all_paths = set()

    def on_paths(self, instance, value):
        for path in self.paths:
            self.add_widget(File(path))
        self.all_paths = self.all_paths.union(self.paths)


class Filechooser(Popup):
    u"""."""

    def __init__(self, targer_widget, *args, **kwargs):
        super(Filechooser, self).__init__(*args, **kwargs)
        self.target = targer_widget

    def add_files_and_dismiss(self):
        u"""."""
        self.target.paths = self.ids['filechooser'].selection
        self.dismiss()
