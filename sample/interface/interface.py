#!usr/bin/env python
# coding: utf-8

'''This is the App intercafe powered by Tkinter.
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
from personalFrame import labelframe
from reportButton import printButton
from openFile import openFileFrame
from context import ANGULOSAPPDIRECTORY

class Root(tk.Tk):

    def __init__(self, title):
        tk.Tk.__init__(self)
        self.title(title)
        self._directory = ANGULOSAPPDIRECTORY
        self._AppColors = ('#9fb9d2', '#5f92d0', '#4b5992')
        self._MasterFrame = tk.Frame(
                self,
                highlightcolor=self._AppColors[2],
                highlightthickness=2
                )
        self._MasterFrame.pack(expand=True)
        self._MasterFrame.focus()
        self.configure(background=self._AppColors[1])
        CentroPantallaX = (self.winfo_screenwidth() / 2) - 105
        CentroPantallaY = (self.winfo_screenheight() / 2) - 105
        geometria = '180x210+{}+{}'.format(CentroPantallaX, CentroPantallaY)
        self.geometry(geometria)
        self.pack_propagate(False)
        return

    def getAppDirectory(self):
        return self._directory

    def getAppColor(self, n):
        return self._AppColors[n]

    def getAppWidth(self):
        return self._AppWidth

    def getPersonalFrame(self):
        return self._personal

    def buildPersonalWidget(self):
        personal = labelframe(self._MasterFrame)
        personal.buildEntrys()
        self._personal = personal
        return

    def buildFileWidget(self):
        fileframe = openFileFrame(self._MasterFrame)

    def buildGenerateButton(self):
        boton = printButton(self._MasterFrame)

if __name__ == '__main__':
    App = Root('Angulos App')
    App.buildPersonalWidget()
    App.buildFileWidget()
    App.buildGenerateButton()
    App.mainloop()

