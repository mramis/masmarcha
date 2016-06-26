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

import logging

import Tkinter as tk

from personalFrame import labelframe
from reportButton import printButton
from openFile import openFileFrame
from textScriptList import textList
from textWidget import Text

class Root(tk.Tk):

    def __init__(self, title, path_tree):
        tk.Tk.__init__(self)
        self.title(title)
        self._directory = path_tree
        self._AppColors = ('#9fb9d2', '#5f92d0', '#4b5992')
        self._files = []
        MasterFrame = tk.Frame(
                self,
                highlightcolor=self._AppColors[2],
                highlightthickness=2
        )
        MasterFrame.grid()
        self.configure(background=self._AppColors[1])
        MasterFrame.focus()
        self._TopLeftFrame = tk.Frame(MasterFrame)
        self._TopRightFrame = tk.Frame(MasterFrame)
        self._LowerFrame = tk.Frame(MasterFrame)
        self._TopLeftFrame.grid(row=0, column=0, ipadx=3)
        self._TopRightFrame.grid(row=0, column=1, ipadx=3)
        self._LowerFrame.grid(row=1, column=0, columnspan=2, pady=5)
        CentroPantallaX = (self.winfo_screenwidth() / 2) - 155
        CentroPantallaY = (self.winfo_screenheight() / 2) - 155
#        geometria = '450x310+{}+{}'.format(CentroPantallaX, CentroPantallaY)
#        self.geometry(geometria)
        self.propagate(False)
        return

    def getAppDirectory(self):
        return self._directory

    def getAppColor(self, n):
        return self._AppColors[n]

    def getAppWidth(self):
        return self._AppWidth

    def getPersonalFrame(self):
        return self._personal

    def getFilesWidget(self):
        return self._fileList

    def getFiles(self):
        return self._files

    def getComment(self):
        return self._comment.get('1.0','4.end')

    def buildPersonalWidget(self):
        personal = labelframe(self._TopLeftFrame)
        personal.buildEntrys()
        self._personal = personal
        return

    def buildFileList(self):
        self._fileList = textList(self._TopRightFrame)
        return

    def buildFileWidget(self):
        fileframe = openFileFrame(self._TopRightFrame)
        return

    def buildCommentWidget(self):
        self._comment = Text(self._LowerFrame)

    def buildGenerateButton(self, functions):
        boton = printButton(self._LowerFrame, functions)
        return


if __name__ == '__main__':
    App = Root('Angulos App')
    App.buildPersonalWidget()
    App.buildFileList()
    App.buildFileWidget()
    App.buildCommentWidget()
    App.buildGenerateButton()
    App.mainloop()

