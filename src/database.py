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
                        notes TEXT,
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

    def id_adder(sid, parameters):
        fullparamters = []
        for param in parameters:
            fullparamters.append(((sid,) + param))
        return fullparamters

    insert_person = """
    INSERT INTO person VALUES (?,?,?,?,?);
    """
    insert_session = """
    INSERT INTO session(pid, day, assistance, test, notes) VALUES (?,?,?,?,?);
    """
    insert_parameters = """
    INSERT INTO parameters(sid, lat, duration, stance, swing, stride, cadency,
    velocity, hip, knee, ankle) VALUES (?,?,?,?,?,?,?,?,?,?,?);
    """

    with sqlite3.connect(database, detect_types=1) as conn:
        cur = conn.cursor()
        try:
            # La persona puede existir dentro de la base de datos, entonces
            # no se agrega, y salta la excepción.
            cur.execute(insert_person, person)

        except sqlite3.IntegrityError:
            logging.error("person-id(%s) existe en %s" % (person[0], database))

        cur.execute(insert_session, (person[0], ) + session)
        cur.executemany(insert_parameters, id_adder(cur.lastrowid, parameters))


def search(database, **kwargs):
    u"""Búsqueda de parámetros cinemáticos.

    Realiza una búsqueda de los parámetros cinemáticos dentro de la base de
    datos según los pares columna, valor que se utlizen como kwargs.
    :param kwargs: pares Columna=Valor.
    :type kwargs: dict
    :return: parámetros cinemáticos.
    :rtype: list
    """
    # Para encontrar los parámetros que buscamos bajo las condiciones que se
    # argumentan en kwargs, primero tenemos que encontrar los identificadores
    # de sesión(sids). Para esto construimos una tabla con la sentencia sql
    # INNER JOIN que junta los valores de las tablas session y person. Sobre
    # esta tabla con la clausula WHERE añadimos las condiciones de busqueda
    # que se pasan en kwargs. El resultado son las sids que nos indican que
    # valores de parameters son los que nos interesan.

    # **kwargs es un diccionario con el nombre de la columna y el valor que
    # se debe buscar dentro de la base de datos para encontrar coincidencias.

    # Este diccionario se utiliza para escoger el nombre de la tabla en la
    # que se encuentra la columna que contiene nuestra búsqueda. La letra
    # mayúscula es el alias de la tabla que se define mas adelante en la
    # sentencia SELECT.
    tab_mapper = {'name': 'P', 'lastname': 'P', 'dx': 'P',
                  'test': 'S', 'assistance': 'S'}

    # Se construyen las condiciones de la clausula WHERE según los
    # pares "col=value" que se ingresan en kwargs.
    values, search_conditions = [], []
    for col, val in kwargs.iteritems():
        if not val:
            continue

        # En la búsqueda por edad se tiene que tomar un rango.
        if col == 'age':
            age_values = re.findall('[0-9]+', val)
            search_conditions.append('P.age >= ? AND P.age <= ?')
            values.append(min(age_values))
            values.append(max(age_values))
            continue

        search_conditions.append(
            '{tab}.{col} = ?'.format(tab=tab_mapper[col], col=col))
        values.append(val)

    # NOTE: Si todos los argumentos en kwargs son cadenas vacias, entonces
    # se sale de la excepción. Hay que ver si este código es necesario.
    if not search_conditions:
        return

    # Se forma el argumento de la clausula WHERE a través del operador AND.
    where_argument = ' AND '.join(search_conditions)

    # Esta es la sentencia base SELECT, que además de obtener los sids,
    # tambien extrae la metadata que debe informar el contexto de los
    # datos.
    select_stmt = """
    SELECT S.id, S.day, P.name, P.lastname, P.dx, S.notes
    FROM session S INNER JOIN person P ON S.pid = P.id WHERE (...)
    """

    with sqlite3.connect(database, detect_types=1) as conn:
        cur = conn.cursor()
        cur.execute(select_stmt.replace('...', where_argument), values)
        fulldata = cur.fetchall()

    # Separamos los sids de la metadata, ademas construimos los argumentos
    # de la clausula WHERE para la sentencia SELECT que extrae los parámetros
    # según los sids.
    metadata = {}
    values, search_conditions = [], []
    for sid, d, n, ln, dx, nt in fulldata:
        search_conditions.append('sid = ?')
        values.append(sid)
        metadata[sid] = (d, n, ln, dx, nt)

    where_argument = ' OR '.join(search_conditions)
    select_stmt = "SELECT * FROM parameters WHERE (...)"

    print select_stmt.replace('...', where_argument)

    with sqlite3.connect(database, detect_types=1) as conn:
        cur = conn.cursor()
        cur.execute(select_stmt.replace('...', where_argument), values)
        parameters = cur.fetchall()

    return metadata, parameters
