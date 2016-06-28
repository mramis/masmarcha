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

from interface.interface import Root
from paths import (ANGULOSAPPDIRECTORY,
                   CASEDIRECTORY,
                   BASEDIRECTORY,
                   TEMPDIRECTORY)
from paths import checkPaths, casePath, copyToBase, clearTemp
from process import (extractJointMarkersArraysFromFiles,
                     extractJointAnglesFromJointMarkersArrays,
                     plotJointAnglesArrays,
                     buildReport)
functions = [
        casePath,
        copyToBase,
        extractJointMarkersArraysFromFiles,
        extractJointAnglesFromJointMarkersArrays,
        plotJointAnglesArrays,
        buildReport,
        clearTemp
]

checkPaths()

root_tree = {'app_path' : ANGULOSAPPDIRECTORY,
             'bases'    : BASEDIRECTORY,
             'casos'    : CASEDIRECTORY,
             'temp'     : TEMPDIRECTORY}

App = Root('Angulos App', root_tree)
App.buildPersonalWidget()
App.buildFileList()
App.buildFileWidget()
App.buildCommentWidget()
App.buildGenerateButton(functions)
App.mainloop()


