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

import os
from datetime import date

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from sequenceString import drawStringSequence
from fonts import addFonts
from paragraph import writeParagraph
from constants import LEFTMARGIN, COMMONMARGINS, COLORS

class baseReport(Canvas):

    def __init__(self, filename, paths, **kwargs):
        Canvas.__init__(self, filename, pagesize=A4)
        self.setTitle('Goniometría de Marcha')
        self._images = paths['image_path']
        self._fonts = addFonts(paths['font_path'])
        self._data = kwargs
        self._data['date'] = '{:%d-%m-%Y}'.format(date.today())
        self._data['pagenumber'] = '01'
        return

    def drawHeader(self):
        # date
        x = LEFTMARGIN
        y = A4[1] - COMMONMARGINS
        self.setFont(self._fonts[5], 10)
        self.setFillColor(COLORS['gray'])
        self.drawString(x, y, self._data['date'])
        # title
        title = u'GONIOMETRÍA DE MARCHA'
        y = A4[1] - COMMONMARGINS*1.6
        self.setFont(self._fonts[4], 29.7)
        self.setFillColor(COLORS['lightblue'])
        self.drawString(x, y, title)
        # personal data
        y -= cm
        fontSeq = ((self._fonts[1], 12),)*2
        colorSeq = (COLORS['red'], COLORS['gray'])
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
        # comment
        if self._data['comment'].strip():
            x += 10; y -= 10
            start_paragraph = x, y + .3*cm
            self.setFont(self._fonts[0], 11)
            self.setStrokeColor(COLORS['gray'])
            self.setFillColor(COLORS['gray'])
            end_paragraph = writeParagraph(self, self._data['comment'], x, y)
            x1, y1 = start_paragraph; x2, y2 = end_paragraph
            self.setStrokeColor(COLORS['gray'])
            self.line(x1 - 7, y1, x2 - 7, y2)
        return

    def drawFootPage(self):
        # constants
        line1 = u'Pág. & {pagenumber} & | & {name} & | & {date}'
        line2 = u'Reporte Goniométrico de la marcha'

        c1, c2 = COLORS['gray'], COLORS['lightblue']
        colorSequence = (c1, c1, c2, c1, c2, c1)

        f1, f2 = (self._fonts[1], 10), (self._fonts[0], 10)
        fontSequence = (f1, f1, f1, f2, f1, f1)

        CreativeCommons = os.path.join(self._images, 'creative-commons.png')
        # first line
        firstLine = line1.format(**self._data)
        sequence = firstLine.split('&')
        y = COMMONMARGINS*0.7
        drawStringSequence(
                self, Y=y,
                stringSequence=sequence,
                fontSequence=fontSequence,
                colorSequence=colorSequence
                )
        # second line
        self.setFillColor(COLORS['red'])
        self.setFont(f1[0], size=8)
        x = A4[0]*0.5
        y = COMMONMARGINS - cm
        self.drawCentredString(x, y, line2)
        # creative commons image
        x = A4[0] - 3*cm
        y = COMMONMARGINS - 1.6*cm
        self.drawImage(CreativeCommons, x, y)
        return

    def drawCharts(self):

        width = 330
        height = 198
        x = LEFTMARGIN
        y = A4[1] - 16*cm
        ref_names = ('cadera.png', 'rodilla.png', 'tobillo.png')
        references = [os.path.join(self._images, ref) for ref in ref_names]
        text_references = '''*Presentación de la goniometría de {} en el plano
        sagital durante un ciclo completo de la marcha humana. Si en la gráfica
        aparecen más de una curva, NO es correcto sacar conclusiones sobre la
        velocidad angular, puesto que se encuentran ligeramente alteradas. Las
        referencias que se observan a la derecha han sido tomadas del libro "The
        biomechanics and motor control of human gait", Winter DA. University of
        Waterloo Press.'''
        for i, plot_name in enumerate(sorted(os.listdir(self._data['plots']))):
            plot = os.path.join(self._data['plots'], plot_name)
            title = os.path.basename(plot).split('_')[1]
        # drawingTitleField
            titleBGSizes = width*0.5, height*0.29
            titleBGXY = x, y + height*0.8
            titleWidth = self.stringWidth(title, self._fonts[0], 11)
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
            self.setFont(self._fonts[0], 11)
            self.setFillColor(COLORS['gray'])
            self.drawString(titleXY[0], titleXY[1], title)
        # drawingPlot
            white = [255, 255, 255, 255, 255, 255]
            self.drawImage(plot, x, y,
                           width=width,
                           height=height,
                           mask=white)
        # drawing reference
            x_ref = x + width + 10
            y_ref = y
            width_ref = width*.45,
            height_ref = height*.45
            self.setFont(self._fonts[5], 7)
            #self.setFontSize(6)
            self.drawString(x_ref, y_ref + height_ref + 5, '*Referencia')
            self.drawImage(references[i], x_ref, y_ref,
                            width=width*.45,
                            height=height*.45)
            texto = text_references.format(ref_names[i].split('.')[0])
            writeParagraph(self,texto, x, y - 10, inter=0.3)

            y -= width*.85
            if i % 2 == 1:
                self.showPage()
                y = A4[1] - (COMMONMARGINS*2 + height)
                pageNumber = int(self._data['pagenumber']) + 1
                self._data['pagenumber'] = '0{}'.format(pageNumber)
                self.drawFootPage()
        return



if __name__ == '__main__':
    import os
    plots = os.path.abspath('/home/mariano/AngulosApp/Casos/Mariano')
    
    context = {'name'   : 'Estefania Lodeiro Urruchaga',
               'age'    : '29 Años',
               'dx'     : 'Sin clínica aparente',
               'comment': 'Habia una vez un loquito que no queria estar mas en soledad y lo único que hacia era divertirse con los caballos y la vieja comadreja de los eucaliptos y las glorietas de madera que tanto le gustaban a su madre.\n',
               'plots'  : plots}

    paths = {'image_path':os.path.abspath('./images'),
             'font_path' :os.path.abspath('./tipografias')}

    pdf = baseReport('pdfTest.pdf', paths, **context)
    pdf.drawHeader()
    pdf.drawFootPage()
    pdf.drawCharts()
    
    pdf.showPage()
    pdf.save()

