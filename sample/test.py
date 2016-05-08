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


from lectura.extractArrays import textToArray
from calculo.joints import hipAngles, kneeAngles, ankleAngles, Direction
from calculo.calculations import polynomialRegression
from documento.charts import timeJointPlot, jointJointPlot

master = textToArray('./lectura/kinoveatext/MPlano.txt')
cadera, rodilla, tobillo, mtt = master

PAngCadera = hipAngles(cadera, rodilla, Direction(master))
PAngRodilla = kneeAngles(cadera, rodilla, tobillo, Direction(master))
PAngTobillo = ankleAngles(rodilla, tobillo, mtt)

master = textToArray('./lectura/kinoveatext/MCinta.txt')
cadera, rodilla, tobillo, mtt = master

AngCadera = hipAngles(cadera, rodilla, Direction(master))
AngRodilla = kneeAngles(cadera, rodilla, tobillo, Direction(master))
AngTobillo = ankleAngles(rodilla, tobillo, mtt)

master = textToArray('./lectura/kinoveatext/TPlano.txt')
cadera, rodilla, tobillo, mtt = master

TPAngCadera = hipAngles(cadera, rodilla, Direction(master))
TPAngRodilla = kneeAngles(cadera, rodilla, tobillo, Direction(master))
TPAngTobillo = ankleAngles(rodilla, tobillo, mtt)

#polyCadera = polynomialRegression(AngCadera, 12)
#polyRodilla = polynomialRegression(AngRodilla, 12)
#polyTobillo = polynomialRegression(AngTobillo, 12)


#timeJointPlot(AngCadera, polyCadera, XLimits=(0, 100), YLimits=(-20, 50), keys='Cadera')
#timeJointPlot(AngRodilla, polyRodilla, XLimits=(0, 100), YLimits=(-10, 70), keys='Rodilla')
#timeJointPlot(AngTobillo, polyTobillo, XLimits=(0, 100), YLimits=(-25, 20), keys='Tobillo')
#
#jointJointPlot(AngCadera, AngRodilla, XLimits=(-20, 50), YLimits=(0, 100),
#keys=('Cadera', 'Rodilla'))
#jointJointPlot(AngRodilla, AngTobillo, XLimits=(-10, 100), YLimits=(-30, 45),
#keys=('Rodilla', 'Tobillo'))
