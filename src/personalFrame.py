#!usr/bin/env python
# coding: utf-8

'''This is the wi to handle the personal information
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
from entryField import entry

class labelframe(tk.LabelFrame):

    def __init__(self, VenMaster):
        tk.LabelFrame.__init__(
                self,
                master=VenMaster,
                text=u'Información Personal',
                )
        self.grid(padx=20, pady=20, sticky='N')

    def buildEntrys(self):
        localFrame = tk.Frame(self)
        localFrame.grid()
        self._name = entry(localFrame, u'NOMBRE', 0, 0, 10)
        self._age = entry(localFrame, u'EDAD', 0, 1, 10)
        self._diagnosis = entry(
                localFrame,
                u'DIAGNÓSTICO'.encode('utf-8')
                , 0, 2, 10
                )


if __name__ == '__main__':
    root = tk.Tk()
    personal = labelframe(root)
    personal.buildEntrys()
    root.mainloop()
