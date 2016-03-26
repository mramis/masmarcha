#!usr/bin/env python
# coding: utf-8

'''This it's the widget to find the output plain text from Kinovea.
'''

# Copyright (C) 2016  Mariano Ramis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import Tkinter as tk
from tkFileDialog import askopenfilename

from folders import HOME

class openFileFrame(tk.Frame):

    def __init__(self, VenMaster):
        tk.Frame.__init__(
                self,
                master=VenMaster,
                )
        self._boton = tk.Button(
                self,
                text='"Abrir Archivo"',
                width=17,
                command=self.abrir
                )
        self._boton.pack(padx=1, pady=5)
        self.pack()
        self._options = {}
        self._options['defaultextension'] = '.txt'
        self._options['filetypes'] = [
                ('text files', '.txt'),
                ('all files', '.*')
                ]
        self._options['initialdir'] = HOME

    def abrir(self):
        self._file = askopenfilename(**self._options)
        try:
            filename = os.path.basename(self._file)
            if filename:
                self._boton.configure(text=filename)
            else:
                self._boton.configure(text='"Abrir Archivo"')
        except:
            pass
