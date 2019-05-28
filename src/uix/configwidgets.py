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


from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout


class ConfigWidget(GridLayout):
    u"""Clase base de widgets de configuración de variables de usuario."""

    def __init__(self, label, section, variable):
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
        except ValueError:
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
