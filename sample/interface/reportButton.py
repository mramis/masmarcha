#!usr/bin/env python
# coding: utf-8

'''This Tkinter Button collect all information and print it.
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
import logging
from datetime import datetime

import Tkinter as tk

class printButton(tk.Button):

    def __init__(self, VenMaster, functions):
        local = tk.Frame(VenMaster)
        tk.Button.__init__(
                self,
                master=local,
                text='Generar',
                width=17,
                command=self.generar
                )
        local.pack(ipadx=1, ipady=5)
        self._functions = functions
        self.pack()
        return

    def generar(self):
        App = self.master.master.master.master
        # Se consiguen los campos de la interface
        name = App.getPersonalFrame()._name.getField().encode('utf_8')
        age = App.getPersonalFrame()._age.getField().encode('utf_8')
        diagnosis = App.getPersonalFrame()._diagnosis.getField().encode('utf_8')
        comment = App.getComment().encode('utf_8')
        files = App.getFiles()

        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.INFO)
        today = datetime.today().strftime('%d-%m-%Y %H:%M')
        logging.info(today)

        if not files: # es lo único indispensable para poder hacer el estudio
            logging.critical('No se encontraron archivos para analizar')
            return
        logging.info('Entrada: {}'.format(str(files)))
        # Se crea(si no existe) el directorio donde se van a guardar los
        # resultados del análisis, en el directorio de la Aplicación, en la
        # sección de Casos.
        temp_path = App._directory['temp']
        save_path = os.path.join(App._directory['casos'], name)
        make_case = 'casePath'
        assert self._functions[0].__name__ == make_case
        self._functions[0](save_path)
        logging.info('Dirección verificada: {}'.format(save_path))

        # Se comienza con la extración de los datos de cada uno de los archivos
        first_step = 'extractJointMarkersArraysFromFiles'
        assert self._functions[2].__name__ == first_step
        try:
            joint_markers_array = self._functions[2](files)
            # Se hace una copia de los archivos utilizados en el análisis
            copy_base = 'copyToBase'
            assert self._functions[1].__name__ == copy_base
            self._functions[1](files, name, comment.strip())
        except:
            return

        # Si se supero la primer instacia de análisis entonces se procede a
        # calcular los ángulos de las articulaciones de MMII.
        try:
            second_step = 'extractJointAnglesFromJointMarkersArrays'
            assert self._functions[3].__name__ == second_step
            joint_angles_array = self._functions[3](joint_markers_array)
        except:
            return

        # Una vez que se tienen los ángulos, se grafican y se guardan en el
        # primero en un directorio temporal para luego ser movidas al definitivo
        # save_path
        third_step = 'plotJointAnglesArrays' 
        elements_in_path = len(os.listdir(save_path))
        code_name = str(elements_in_path/3 + 1)
        temp_name = os.path.join(App._directory['temp'], code_name)
        assert self._functions[4].__name__ == third_step
        self._functions[4](joint_angles_array, name=temp_name)
        logging.info('Se generaron las gráficas en {}'.format(temp_path))

        # Se construye el reporte en el directorio temporal de donde se sacan
        # las gráficas.
        fourth_step = 'buildReport'
        assert self._functions[5].__name__ == fourth_step
        data = {'name'   : name,
                'age'    : age,
                'dx'     : diagnosis,
                'comment': comment,
                'plots'  : temp_path}
        self._functions[5](temp_name, data)

        # Para finalizar se mueven las gráficas del directorio temporal a 
        # save_path
        last_step = 'clearTemp'
        assert self._functions[6].__name__ == last_step
        self._functions[6](save_path)
        logging.info('Se movieron las gráficas as {}'.format(save_path))
        logging.info('Se ha terminado con éxito la aplicación\n')


