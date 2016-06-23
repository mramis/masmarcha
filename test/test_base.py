#!usr/bin/env python
# coding: utf-8

'''perform a test.
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

import numpy as np

from context import sqlite


try:
    base = sqlite.dataBase('test')
    base.buildTabla(32391104)
    base.close()
except:
    print 'base already exists'


person = {'date'        : str(date.today()),
          'name'        : u'mariano andrés ramis',
          'age'         : u'29',
          'dx'          : u'Brujulitis',
          'hipAngles'   : np.array((1.,2.)),
          'kneeAngles'  : np.array((2.,3.)),
          'ankleAngles' : np.array((3.,4.))}

base = sqlite.dataBase('test')
base.insertIntoTable(32391104, person)
base.close()



base = sqlite.dataBase('test')
table = base.selectFromTable(32391104)
print table
