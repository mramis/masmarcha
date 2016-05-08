#!usr/bin/env python
# coding: utf-8

'''The Header of "report".pdf
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

from constants import colors, leftMargin, commonMargins, A4, cm
from footPage import drawStringSequence
from fonts import Fonts

def drawHeader(canvas, X=0, Y=0, **kwargs):
    keywordArgs = kwargs.keys()
    KWARGS = ('date', 'data', 'pageNumber')
    TrueList = [key in KWARGS for key in keywordArgs]
    if kwargs and not all(TrueList):
        message = ('KeywordArgs must be: date, data, and pageNumber.')
        raise Exception(message)

    date = kwargs['date']
    pageNumber = kwargs['pageNumber']
    personalData = kwargs['data']

# date
    X = leftMargin
    Y = A4[1] - commonMargins
    canvas.setFont(Fonts[5], 10)
    canvas.setFillColor(colors['grey'])
    canvas.drawString(X, Y, date)
# title
    title = u'GONIOMETRÍA DE MARCHA'
    Y = A4[1] - commonMargins*1.6
    canvas.setFont(Fonts[4], 29.7)
    canvas.setFillColor(colors['lightblue'])
    canvas.drawString(X, Y, title)
# personal data
    Y -= cm
    fontSeq = ((Fonts[1], 12),)*2
    colorSeq = (colors['red'], colors['grey'])
    keys = ('Nombre ', 'Edad ', 'Dx ')
    for key in keys:
        string = (key, personalData[key])
        drawStringSequence(
                canvas, X, Y,
                stringSequence=string,
                fontSequence=fontSeq,
                colorSequence=colorSeq
                )
        Y -= cm*0.7
    return



if __name__ == '__main__':
    import reportlab.pdfgen.canvas as canvas
    pdf = canvas.Canvas('HeaderTest.pdf')
    personal = {'Nombre ' : u'Mariano Ramis',
                'Edad '  : u'29',
                'Dx '   : u'Nada'}
    context = {'pageNumber' : '01',
               'data'       : personal,
               'date'       : '12.03.1999'}
    drawHeader(pdf, **context)
    pdf.showPage()
    pdf.save()
