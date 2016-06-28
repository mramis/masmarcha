#!usr/bin/env python
# coding: utf-8

'''Script to build the foot page of the "report".pdf
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


from reportlab.lib.pagesizes import A4

def drawStringSequence(canvas, X=0, Y=0, **kwargs):    
    SWidth = canvas.stringWidth
    keywordArgs = kwargs.keys()
    KWARGAS = ('colorSequence', 'fontSequence', 'stringSequence')
    TrueList = [key in KWARGAS for key in keywordArgs]
    if kwargs and not all(TrueList):
        message = ('KeywordArgs must be: ',
                   'colorSequence, '      ,
                   'fontSequence, '      ,
                   'and stringSequence.'  )
        raise Exception(''.join(message))
    
    fonts = kwargs['fontSequence']
    colors = kwargs['colorSequence']
    stringSeq = kwargs['stringSequence']

    F = fonts[0]
    wordsWidth = [SWidth(word, F[0], F[1]) for word in stringSeq]
    length = sum(wordsWidth)
    if not X:
        X = (A4[0] - length)*0.5

    for i, word in enumerate(stringSeq):
        width = SWidth(word, fonts[i][0], fonts[i][1])
        canvas.setFont(fonts[i][0], fonts[i][1])
        canvas.setFillColor(colors[i])
        canvas.drawString(X, Y, word)
        X += width
    return

