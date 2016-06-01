#!usr/bin/env python
# coding: utf-8

'''Especial tk.Entry with methods defined to get the field information
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

class entry(tk.Entry):

    def __init__(self, VenMaster, field):
        labelFrame = tk.Frame(
                VenMaster,
                )
        labelFrame.pack(expand=True)
        entryFrame = tk.Frame(
                VenMaster,
                )
        entryFrame.pack()
        tk.Entry.__init__(
                self,
                master=entryFrame
                )
        var = tk.StringVar(self)
        self.configure(textvariable=var)
        label = tk.Label(
                labelFrame,
                text=field,
                )
        label.pack(expand=True)
        self.pack()

    def getField(self):
        return self.get()

