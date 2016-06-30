#!/usr/bin/env python
# coding: utf-8

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

from reportlab.lib.units import cm

def writeParagraph(canvas, text, x, y, inter=0.5, width_limit=450):
    '''Escribe un párrafo de una cadena de texto.
    Args:
        canvas: es el objeto de ``canvas.Canvas`` de reportlab ya iniciado.
        text: es el texto a dibujar.
        x, y: pociciones donde se inicia el texto.
        inter: escalar de cm para el interlineado.
        width_limit: el ancho del parrafo, por defecto=450 es aproximadamente
            un ancho de hoja A4 menos 5 cm.
    Returns:
        x, y: la última posición del cursor, en la última línea del párrafo.
    '''
    cumulative_words_width = 0
    i = 0
    for j, word in enumerate(text.split()):
        cumulative_words_width += canvas.stringWidth(word + ' ')
        if cumulative_words_width > width_limit:
            canvas.drawString(x, y, ' '.join(text.split()[i:j]))
            y -= inter*cm
            cumulative_words_width = 0
            i = j
    canvas.drawString(x, y, ' '.join(text.split()[i:]))
    return (x, y)

if __name__ == '__main__':
    text = '''
    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
    from reportlab.pdfgen import canvas
    pdf = canvas.Canvas('test')
    writeParagraph(pdf, text, 2*cm, 400)
    pdf.showPage()
    pdf.save()
