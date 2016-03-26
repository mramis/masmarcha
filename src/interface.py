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
from folders import ANGULOSAPPDIRECTORY
from personalFrame import labelframe
from reportButton import printButton
from openFile import openFileFrame

class Root(tk.Tk):

    def __init__(self, title):
        tk.Tk.__init__(self)
        self.title(title)
        self._AppColor = '#5f92d0'
        self.configure(background=self._AppColor)
        self._directory = ANGULOSAPPDIRECTORY 
        return

    def getAppDirectory(self):
        return self._directory

    def getAppColor(self):
        return self._AppColor

    def getAppWidth(self):
        return self._AppWidth

    def getPersonalFrame(self):
        return self._personal

    def buildPersonalWidget(self):
        personal = labelframe(self)
        personal.buildEntrys()
        self._personal = personal
        return

    def buildFileWidget(self):
        fileframe = openFileFrame(self)

    def buildGenerateButton(self):
        boton = printButton(self)

if __name__ == '__main__':
    App = Root('Angulos App')
    App.buildPersonalWidget()
    App.buildFileWidget()
    App.buildGenerateButton()
    App.mainloop()

