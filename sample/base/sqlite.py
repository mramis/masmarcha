#!usr/bin/env python
# coding: utf-8

'''Base sqlite defined here to store datasets, strings must be
lowercase and unicode type and arrays must be Numpy Arrays.
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


import sqlite3

import numpy as np

class dataBase:

    def __init__(self, name):
        self._connection = sqlite3.connect('{}.db'.format(name))
        self._cursor = self._connection.cursor()
        return

    def buildTabla(self, DNI):
        command = '''CREATE TABLE _{} (
                  date CHAR(10),
                  Name CHAR(50),
                  Age CHAR(10),
                  Dx CHAR(50),
                  hipAngles BLOB,
                  kneeAngles BLOB,
                  ankleAngles BLOB);
                  '''.format(DNI)
        self._cursor.execute(command)
        self._connection.commit()
        return

    def insertIntoTable(self, DNI, personalData):
        command = ''' INSERT INTO _{}
                  (date, Name, Age, Dx,
                  hipAngles, kneeAngles, ankleAngles)
                  VALUES (?, ?, ?, ?, ?, ?, ?)
                  '''.format(DNI)
        self._cursor.execute(
                command,
                (personalData['date'],
                 personalData['name'],
                 personalData['age'],
                 personalData['dx'],
                 personalData['hipAngles'].tostring(),
                 personalData['kneeAngles'].tostring(), 
                 personalData['ankleAngles'].tostring())
        )
        self._connection.commit()
        return

    def selectFromTable(self, DNI):
        command = '''SELECT * FROM _{}
                  '''.format(DNI)
        self._connection.text_factory = str
        self._cursor.execute(command)
        data = self._cursor.fetchall()
        times = []
        for item in data:
            personalData = {'date'        : item[0],
                            'name'        : item[1],
                            'age'         : item[2],
                            'dx'          : item[3],
                            'hipAngles'   : np.fromstring(item[4]),
                            'kneeAngles'  : np.fromstring(item[5]),
                            'ankleAngles' : np.fromstring(item[6])}
            times.append(personalData)
        return times

    def close(self):
        self._connection.close()
        return
