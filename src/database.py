#!/usr/bin/env python
# coding: utf-8

"""Docstring."""

# Copyright (C) 2017  Mariano Ramis

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import sqlite3
import re
import io

import numpy as np


# logging setup
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = '[%(name)10s line:%(lineno)d] - %(levelname)-8s - %(message)s'
handler.setFormatter(logging.Formatter(formatter))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# Este fragmento es la solución que encontré en stackoverflow para almacenar
# arreglos numpy en las tablas sqlite.
# http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
def adapt_array(ndarray):
    out = io.BytesIO()
    np.save(out, ndarray)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(blob):
    out = io.BytesIO(blob)
    out.seek(0)
    return np.load(out)


# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)
# Converts TEXT to np.array when selecting
sqlite3.register_converter("ARRAY", convert_array)


def create(database):
    u"""Crea un archivo sql.

    El archivo sql contiene las tablas person, donde se alojan los datos de
    cada persona, session, que contiene los datos de una sesión de trabajo,
    y parameters, que son los parámetros de marcha que se obtuvieron en las
    distintas sesiones.
    :param database: ruta del destino de la base de datos sql.
    :type database: str
    """
    # Este código se encarga de la creación de la base de datos y de las
    # tablas que contienen toda la información de la aplicación. Se realiza
    # por única vez cuando se corre el archivo setup.
    with sqlite3.connect(database, detect_types=1) as conn:
        conn.execute("""CREATE TABLE person(
                        id TEXT PRIMARY KEY NOT NULL,
                        lastname TEXT NOT NULL,
                        name TEXT NOT NULL,
                        age TEXT NOT NULL,
                        dx TEXT NOT NULL)""")

        conn.execute("""CREATE TABLE session(
                        id INTEGER PRIMARY KEY NOT NULL,
                        pid TEXT NOT NULL,
                        day DATE NOT NULL,
                        assistance TEXT,
                        test TEXT,
                        note TEXT,
                        FOREIGN KEY(pid) REFERENCES person(id))""")

        conn.execute("""CREATE TABLE parameters (
                        id INTEGER PRIMARY KEY NOT NULL,
                        sid INTEGER NOT NULL,
                        lat CHAR,
                        duration REAL,
                        stance REAL,
                        swing REAL,
                        stride REAL,
                        cadency REAL,
                        velocity REAL,
                        hip ARRAY,
                        knee ARRAY,
                        ankle ARRAY,
                        FOREIGN KEY(sid) REFERENCES session(id))""")


def insert(database, person, session, parameters):
    u"""Agrega datos a la base.

    :param database: ruta del destino de la base de datos sql.
    :param person: vector con los datos de la persona a quién se le realiza el
     estudio, (id, nombre, apellido, edad, diagnóstico).
    :type person: tuple
    :param session: vector con los datos de sesión, (fecha, tipo de asistencia,
     tipo de prueba, notas de session).
    :type session: tuple
    :param parameters: vector con los resultados del motor de análisis, (
     lateralidad, duración del ciclo, fase de apoyo, fase de balanceo, long. de
     zancada, cadencia, velocidad media, arreglo de cadera, arreglo de rodilla,
     arreglo de tobillo).
    :type parameters: tuple
    """
    with sqlite3.connect(database, detect_types=1) as conn:
        cur = conn.cursor()
        # La persona puede existir(id), por eso está en un try-except.
        try:
            cur.execute("INSERT INTO person VALUES (?,?,?,?,?)", person)
        except sqlite3.IntegrityError:
            logging.error("person-id(%s) existe en %s" % (person[0], database))

        cur.execute("""
            INSERT INTO session(pid, day, assistance, test, note)
            VALUES (?,?,?,?,?)""", (person[0], ) + session)

        insert_stmt = """
            INSERT INTO parameters(sid, lat, duration, stance, swing, stride,
            cadency, velocity, hip, knee, ankle)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)"""
        # NOTE: Existe un comando executemany para ingresar varios valores
        # al mismo tiempo y así evitar el bucle for, pero necesito agregar
        # la letra de lateralidad a los parámetros. Fijarse en el motor para
        # modificar esto.
        sid = cur.lastrowid
        for idy, spt, angles in parameters:
            cur.execute(insert_stmt, (sid, idy[0]) + spt + tuple(angles))


def search(database, **kwargs):
    u"""Búsqueda de parámetros cinemáticos.

    Realiza una búsqueda de los parámetros cinemáticos dentro de la base de
    datos según los pares columna, valor que se utlizen como kwargs.
    :param kwargs: pares Columna=Valor.
    :type kwargs: dict
    :return: parámetros cinemáticos.
    :rtype: list
    """
    # Los kwargs son pares columna=valor para la busqueda en las
    # tablas sesion y persona.
    tab_mapper = {'name': 'person', 'lastname': 'person', 'dx': 'person',
                  'test': 'session', 'assistance': 'session'}

    # Se construyen las condiciones de la clausula WHERE según los
    # parámetros que se ingresan en kwargs.
    values, search_conditions = [], []
    try:
        for col, val in kwargs.iteritems():
            if not val:
                continue

            # En la búsqueda por edad se tiene que tomar un rango.
            if col == 'age':
                age_values = re.findall('[0-9]+', val)
                search_conditions.append('person.age >= ? AND person.age <= ?')
                values.append(min(age_values))
                values.append(max(age_values))
                continue

            search_conditions.append(
                '{tab}.{col} = ?'.format(tab=tab_mapper[col], col=col))
            values.append(val)
    # Este except está puesto porque no existe control sobre las claves
    # de kwargs.
    except KeyError as error:
        logging.error('Mala columna: %s' % error)
        return

    if not search_conditions:
        return

    where_argument = ' AND '.join(search_conditions)
    select_session_ids = """
        SELECT session.id, session.day, person.name, person.lastname
        FROM person INNER JOIN session
        ON person.id = session.pid WHERE (...)
        """.replace('...', where_argument)

    parameters = []
    # NOTE: rendimiento: Se está consultando a la base de datos por cada
    # sid para poder asociarla a cada metadata. La metadata es necesaria
    # para poderidentificar los datos en las gráficas. Tratar de optimizar
    with sqlite3.connect(database, detect_types=1) as conn:
        cur = conn.cursor()
        cur.execute(select_session_ids, values)
        for sid, date, name, lastname in cur.fetchall():
            cur.execute("SELECT * FROM parameters WHERE sid = ?", (sid,))
            meta = [date, ' '.join((name, lastname))]
            parameters.append((meta, cur.fetchall()))
    return parameters
