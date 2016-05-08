#!usr/bin/env python
# coding: utf-8

'''DOCSTRING
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


from fonts import Fonts
from constants import colors

def drawChart(canvas, plot, x, y, width, height, title):

# drawingTitleField
    titleBGSizes = width*0.5, height*0.29
    titleBGXY = x, y + height*0.8
    titleWidth = canvas.stringWidth(title, Fonts[0], 11)
    titleXY = x + (titleBGSizes[0] - titleWidth)*0.5, y + height*1.005
    canvas.setFillColor('#DCDCDD')
    canvas.roundRect(x, y + height*0.8,
                     width=width*0.5,
                     height=height*0.29,
                     radius=15,
                     stroke=0,
                     fill=1)

    canvas.setFont(Fonts[0], 11)
    canvas.setFillColor(colors['grey'])
    canvas.drawString(titleXY[0], titleXY[1], title)

# drawingChartField
    canvas.setFillColor('#F5F5F5')
    canvas.roundRect(x, y,
                     width=width,
                     height=height,
                     radius=10,
                     stroke=0,
                     fill=1)
# drawingPlot
    white = [255, 255, 255, 255, 255, 255]
    canvas.drawImage(plot, x, y, width=width, height=height, mask=white)
    return


if __name__ == '__main__':
    from reportlab.pdfgen import canvas
    pdf = canvas.Canvas('bodyTest.pdf')
    plot = './muestra/Cadera.png'
    drawChart(pdf, plot, 200, 500, 250, 150, 'Rodilla(t)')
    pdf.showPage()
    pdf.save()
