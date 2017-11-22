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


from os import listdir
from os.path import basename, join, abspath
from json import load

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, StringProperty


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


class Schema(Button):
    u"""."""

    def __init__(self, name, popup, *args, **kwargs):
        super(Schema, self).__init__(*args, **kwargs)
        self.id = name
        self.text = basename(name.split('.')[0])
        self.indicator = self.text.split('-')[1]
        self.target = popup

    def choose(self):
        u"""."""
        self.target.current_schema = self.id
        self.target.dismiss()


class PathsViewer(GridLayout):
    u"""."""
    paths = ListProperty([])
    all_paths = set()

    def on_paths(self, instance, value):
        for path in self.paths:
            self.add_widget(File(path))
        self.all_paths = self.all_paths.union(self.paths)

    def refresh(self):
        u"""."""
        text_input = self.parent.parent.ids['pathsgroup']
        text_input.text = text_input.default_message
        self.clear_widgets()
        self.all_paths.clear()


class Filechooser(Popup):
    u"""."""

    def __init__(self, targer_widget, *args, **kwargs):
        super(Filechooser, self).__init__(*args, **kwargs)
        self.target = targer_widget

    def add_files_and_dismiss(self):
        u"""."""
        self.target.paths = self.ids['filechooser'].selection
        self.dismiss()


class SchemaChooser(Popup):
    u"""."""
    current_schema = StringProperty('')

    def __init__(self, indicator_widget, config, *args, **kwargs):
        super(SchemaChooser, self).__init__(*args, **kwargs)
        self.target = indicator_widget
        self.config = config
        self.list_schemas(config.get('paths', 'schemas'))

    def list_schemas(self, path):
        u"""."""
        self.schemas = {}
        self.schemas_path = path
        for json_sch in listdir(path):
            with open(join(abspath(path), json_sch)) as schema:
                self.schemas[json_sch] = load(schema)
            self.ids['schemaslist'].add_widget(Schema(json_sch, self))

    def on_current_schema(self, instance, value):
        u"""."""
        schema_indicator = self.current_schema.split('.')[0].split('-')[1]
        path = join(abspath(self.schemas_path), self.current_schema)
        self.target.text = schema_indicator
        self.config.set('capture', 'schema_indicator', schema_indicator)
        self.config.set('capture', 'schema_path', path)
        self.config.write()
