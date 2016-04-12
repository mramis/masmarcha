#!usr/bin/env python
# coding: utf-8

'''Here it's defined the class report to build a pdf paper
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

from datetime import date

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from graphics import chartBackground

class report(Canvas):

    def __init__(self, filename):
        Canvas.__init__(self, filename, pagesize=A4)
        self.setTitle('REPORTE SIMPLE DE MARCHA')
        self._heightUnit = A4[1] / 30.0
        self._widthUnit = A4[0] / 21.0
        self._leftMargin = inch
        self._bottomMargin = inch
        self._anotherMargins = inch * .8
        self._lastCursorPosition = None
        self._printsHeight = (A4[1] - self._anotherMargins - self._bottomMargin) / 3.0
        self._sectors = {
                'bottom' : (self._leftMargin, self._bottomMargin),
                'middle' : (self._leftMargin, self._printsHeight +
                self._anotherMargins),
                'top'    : (self._leftMargin, self._printsHeight*2 +
                self._anotherMargins)
                }

    def introduceTitle(self):
        Title = (u'REPORTE GONIOMÉTRICO DE MARCHA')
        titleWidth = self.stringWidth(Title)
        X = (A4[0] - titleWidth) / 2.0
        Y = A4[1] - self._leftMargin
        self.drawString(X, Y, Title)

    def introducePersonalData(self, Data):
        today = str(date.today()).split('-')
        today.reverse()
        X = self._leftMargin
        Y = A4[1] - self._heightUnit*4.0
        self.drawString(X, Y, ('{}-{}-{}'.format(*today)))
        Y -= self._heightUnit
        order = ('Nombre', 'Edad', 'Dx')
        for field in order:
            self.drawString(X, Y, '{}: {}'.format(field, Data[field]))
            Y -= self._heightUnit*0.7
        self._lastCursorPosition = X, Y

    def introducePlots(self, plotList):
        listSize = len(plotList)
        X, Y = self._lastCursorPosition
        Y -= 100
        for index, sector in enumerate(('middle', 'bottom')):
            x, y = self._sectors[sector]
            chartBackground(self, x, y, 300, 180, 'nada')
            white = [255, 255, 255, 255, 255, 255]
            self.drawImage(plotList[index], x, y, width=300, height=180, mask=white)

if __name__ == '__main__':
    import os
    plots = [
            os.path.join(os.path.abspath('./muestra'), dirpath)
            for dirpath in os.listdir('./muestra')
            ]
    print plots
    DatosPersonales = {'Nombre':'Mariano',
                       'Edad':'29',
                        'Dx':'Nada'}
    pdf = report('pdftest.pdf')
    pdf.introduceTitle()
    pdf.introducePersonalData(DatosPersonales)
    pdf.introducePlots(plots)
    pdf.showPage()
    pdf.save()
