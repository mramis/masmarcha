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


from kivy.uix.gridlayout import GridLayout
from kivy.properties import (BooleanProperty, StringProperty, NumericProperty,
                             ListProperty)


class ConfigWidget(GridLayout):
    u"""Clase base de widgets de configuración de variables de usuario."""
    label = StringProperty("")
    current_value = None
    section_variable = StringProperty("")

    def on_label(self, instance, value):
        self.ids.label.text = value

    def on_section_variable(self, instance, value):
        self.section, self.variable = value.split(":")
        self.current_value = self.config.get(self.section, self.variable)

    def on_current_value(self, instance, value):
        return NotImplemented

    def writeConfig(self):
        with open(self.config.get("paths", "configfile"), "w") as fh:
            self.config.write(fh)


class BoolOption(ConfigWidget):
    u"""Widget para ajustes de configuración de tipo Boleano."""
    current_value = BooleanProperty(None)

    def on_current_value(self, instance, value):
        if not isinstance(value, bool):
            value = True if value == "True" else False
        self.config.set(self.section, self.variable, str(value))
        self.ids.toggle.state = "down" if value is True else "normal"
        self.writeConfig()

    def change_option(self, state):
        self.current_value = True if state == "down" else False


class IntegerOption(ConfigWidget):
    u"""Widget para ajustes de configuración Numérico de tipo entero."""
    current_value = NumericProperty(1)
    option_values = ListProperty([])

    def on_current_value(self, instance, value):
        self.config.set(self.section, self.variable, str(int(value)))
        self.ids.input.text = "{:.2f}".format(self.current_value)
        self.writeConfig()

    def on_option_values(self, instance, values):
        self.minvalue, self.maxvalue, self.interval = values

    def validate_input(self):
        try:
            self.change_option(int(self.ids.input.text))
        except ValueError:
            self.current_value = self.minvalue
            self.ids.input.text = "{:.2f}".format(self.current_value)

    def change_option(self, value):
        if value <= self.minvalue:
            self.current_value = self.minvalue
            self.ids.input.text = "{:.2f}".format(self.current_value)
        elif value > self.maxvalue:
            self.current_value = self.maxvalue
            self.ids.input.text = "{:.2f}".format(self.current_value)
        else:
            self.current_value = value

    def up_change_option(self):
        self.change_option(self.current_value + self.interval)

    def down_change_option(self):
        self.change_option(self.current_value - self.interval)


class FloatOption(IntegerOption):
    u"""Widget para ajustes de configuración Numérico de tipo flotante."""

    def on_current_value(self, instance, value):
        self.config.set(self.section, self.variable, str(float(value)))
        self.ids.input.text = "{:.2f}".format(self.current_value)
        self.writeConfig()

    def validate_input(self):
        try:
            self.change_option(float(self.ids.input.text))
        except ValueError:
            self.current_value = self.minvalue


class listOption(ConfigWidget):
    u"""Widget para ajustes de configuración de tipo opciones establecidas."""
    current_value = StringProperty("")

    def on_current_value(self, instance, value):
        self.config.set(self.section, self.variable, str(value))
        self.writeConfig()

    def change_option(self):
        self.current_value = self.ids.optionsvalue.text
