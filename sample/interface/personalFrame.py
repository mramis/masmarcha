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

class labelframe(tk.Frame):

    def __init__(self, VenMaster):
        tk.Frame.__init__(
                self,
                master=VenMaster,
                background=VenMaster.master.master.getAppColor(0))
        self.pack(side='left')

    def buildEntrys(self):
        localFrame = tk.Frame(self)
        localFrame.pack()
        self._name = entry(localFrame, u'Nombre')
        self._age = entry(localFrame, u'Edad')
        self._diagnosis = entry(localFrame, u'Diagnóstico'.encode('utf-8'))

