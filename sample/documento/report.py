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
from reportlab.lib.units import cm

from sequenceString import drawStringSequence
from fonts import Fonts
from constants import (TYPOGRAPHYS, IMAGES,
                       leftMargin, commonMargins,
                       heightUnit, widthUnit,
                       colors)

class baseReport(Canvas):

    def __init__(self, filename, **kwargs):
        Canvas.__init__(self, filename, pagesize=A4)
        self.setTitle('Goniometría de Marcha')
        self._data = kwargs
        self._data['date'] = '{:%d-%m-%Y}'.format(date.today())
        self._data['pagenumber'] = '01'
        return

    def drawHeader(self):
# date
        x = leftMargin
        y = A4[1] - commonMargins
        self.setFont(Fonts[5], 10)
        self.setFillColor(colors['grey'])
        self.drawString(x, y, self._data['date'])
# title
        title = u'GONIOMETRÍA DE MARCHA'
        y = A4[1] - commonMargins*1.6
        self.setFont(Fonts[4], 29.7)
        self.setFillColor(colors['lightblue'])
        self.drawString(x, y, title)
# personal data
        y -= cm
        fontSeq = ((Fonts[1], 12),)*2
        colorSeq = (colors['red'], colors['grey'])
        keys = ('name', 'age', 'dx')
        tags = ('Nombre ', 'Edad ', 'Dx ')
        for i, key in enumerate(keys):
            try:
                string = (tags[i], self._data[key])
            except:
                string = (key, 'Anonimous')
            drawStringSequence(
                      self, x, y,
                      stringSequence=string,
                      fontSequence=fontSeq,
                      colorSequence=colorSeq
                      )
            y -= cm*0.7
        return

    def drawFootPage(self):
# constants
        line1 = u'Pág. & {pagenumber} & | & {name} & | & {date}'
        line2 = u'Reporte Goniométrico de la marcha'

        c1, c2 = colors['grey'], colors['lightblue']
        colorSequence = (c1, c1, c2, c1, c2, c1)

        f1, f2 = (Fonts[1], 10), (Fonts[0], 10)
        fontSequence = (f1, f1, f1, f2, f1, f1)

        CreativeCommons = os.path.join(IMAGES, 'creative-commons.png')
# first line
        firstLine = line1.format(**self._data)
        sequence = firstLine.split('&')
        y = commonMargins*0.7
        drawStringSequence(
                self, Y=y,
                stringSequence=sequence,
                fontSequence=fontSequence,
                colorSequence=colorSequence
                )
# second line
        self.setFillColor(colors['red'])
        self.setFont(f1[0], size=8)
        x = A4[0]*0.5
        y = commonMargins - cm
        self.drawCentredString(x, y, line2)
# creative commons image
        x = A4[0] - 3*cm
        y = commonMargins - 1.6*cm
        self.drawImage(CreativeCommons, x, y)
        return

    def drawCharts(self):

        width = 300
        height = 180

        x = leftMargin
        y = A4[1] - 14*cm
        
        for i, plot in enumerate(self._data['plots']):
            title = os.path.basename(plot).split('.')[0]

# drawingTitleField
            titleBGSizes = width*0.5, height*0.29
            titleBGXY = x, y + height*0.8
            titleWidth = self.stringWidth(title, Fonts[0], 11)
            titleXY = (x + (titleBGSizes[0] - titleWidth)*0.5,
                       y + height*1.005)
            self.setFillColor('#DCDCDD')
            self.roundRect(x, y + height*0.8,
                           width=width*0.5,
                           height=height*0.29,
                           radius=15,
                           stroke=0,
                           fill=1)
# drawingChartField
            self.setFillColor('#F5F5F5')
            self.roundRect(x, y,
                           width=width,
                           height=height,
                           radius=10,
                           stroke=0,
                           fill=1)
# drawing title
            self.setFont(Fonts[0], 11)
            self.setFillColor(colors['grey'])
            self.drawString(titleXY[0], titleXY[1], title)
# drawingPlot
            white = [255, 255, 255, 255, 255, 255]
            self.drawImage(plot, x, y,
                           width=width,
                           height=height,
                           mask=white)
            y -= width
            
            if i % 2 == 1:
                self.showPage()
                y = A4[1] - 14*cm
                pageNumber = int(self._data['pagenumber']) + 1
                self._data['pagenumber'] = '0{}'.format(pageNumber)
                self.drawHeader()
                self.drawFootPage()

        return



if __name__ == '__main__':
    import os
    plots = [
            os.path.join(os.path.abspath('/home/mariano/AngulosApp/Casos/Mariano'), dirpath)
            for dirpath in os.listdir('/home/mariano/AngulosApp/Casos/Mariano')
            ]
    
    context = {'name'  : 'Estefania Lodeiro Urruchaga',
               'age'   : '29 Años',
               'dx'    : 'Sin clínica aparente',
               'plots' : plots}

    pdf = baseReport('pdfTest.pdf', **context)
    pdf.drawHeader()
    pdf.drawFootPage()
    pdf.drawCharts()
    
    pdf.showPage()
    pdf.save()

