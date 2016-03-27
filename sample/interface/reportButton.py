#!usr/bin/env python
# coding: utf-8

'''This Tkinter Button collect all information and print it.
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


import Tkinter as tk

class printButton(tk.Button):

    def __init__(self, VenMaster):
        local = tk.Frame(VenMaster)
        tk.Button.__init__(
                self,
                master=local,
                text='Generar',
                width=17,
                command=self.generar
                )
        local.pack(ipadx=1, ipady=5)
        self.pack()

    def generar(self):
        App = self.master.master.master
        personal = App.getPersonalFrame()
        entryName = personal._name.getField()
        entryAge = personal._age.getField()
        entryDiagnosis = personal._diagnosis.getField()
        print entryName, entryAge, entryDiagnosis

  
