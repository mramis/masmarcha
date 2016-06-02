#!/usr/bin/env python
# coding: utf-8

'''Docstring
'''

# Copyright (C) 2016  Mariano Ramis

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


import Tkinter as tk

class Text(tk.Text):

    def __init__(self, VenMaster):
        local = tk.Frame(VenMaster)
        local.pack(pady=8)
        label = tk.Label(
                local,
                text='Reseña:(opcional, ~150 caracteres)'
                )
        label.pack(anchor='w')
        tk.Text.__init__(
                self,
                master=local,
                height=4,
                width=50,
                wrap='word',
                )
        self.pack()
        return

