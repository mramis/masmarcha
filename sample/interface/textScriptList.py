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

class textList(tk.Listbox):

    def __init__(self, VenMaster):
        local = tk.Frame(VenMaster)
        local.pack()
        label = tk.Label(local, text='Archivos')
        label.pack(side='top')
        yscrollbar = tk.Scrollbar(local)
        yscrollbar.pack(side='right', fill='y')
        tk.Listbox.__init__(
                self,
                master=local,
                height=4,
                yscrollcommand=yscrollbar.set
        )
        self.bind('<Key>', self.deleteFile)
        self.pack()
        self.propagate(False)

    def deleteFile(self, event):
        App = self.master.master.master.master
        if event.keycode is 22 or event.keycode is 119:
            try:
                index = self.curselection()[0]
                self.delete(index)
                App._files.pop(index)
            except:
                print('No existe elemento para borrar')
        return


if __name__ == '__main__':
    top = tk.Tk()
    lista = textList(top)

    top.mainloop()
