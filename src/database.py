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

import sqlite3

import numpy as np
import io


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


def create(filename):
    u"""."""
    # Este código se encarga de la creación de la base de datos y de las
    # tablas que contienen toda la información de la aplicación. Se realiza
    # por única vez cuando se corre el archivo setup.
    with sqlite3.connect(filename, detect_types=1) as conn:
        cursor = conn.cursor()
        # Se tienen que crear tres tablas según el diagrama de relaciones.
        # La primer tabla es la de persona.
        cursor.execute("""CREATE TABLE person
                          (pid TEXT PRIMARY KEY NOT NULL,
                           fullname TEXT,
                           age TEXT NOT NULL,
                           dx TEXT NOT NULL)""")
        # La pŕoxima tabla es la de estudio.
        cursor.execute("""CREATE TABLE session
                          (sid INT PRIMARY KEY NOT NULL,
                           personid TEXT,
                           day DATE,
                           assistance TEXT,
                           test TEXT,
                           archive TEXT,
                           FOREIGN KEY(personid) REFERENCES person(pid))
                           """)
        # la última tabla es la parámetros.
        cursor.execute("""CREATE TABLE parameters (
                          cid INT PRIMARY KEY NOT NULL,
                          sessionid INT,
                          laterality CHAR,
                          duration REAL,
                          stance REAL,
                          swing REAL,
                          stride REAL,
                          cadency REAL,
                          velocity REAL,
                          hip ARRAY,
                          knee ARRAY,
                          ankle ARRAY,
                          FOREIGN KEY(sessionid) REFERENCES session(sid))
                          """)


def insert(filename, person, session, parameters):
    u"""."""
    with sqlite3.connect(filename, detect_types=1) as conn:
        cursor = conn.cursor()
        # Si la persona no está en la base de datos entonces se agrega.
        cursor.execute("SELECT pid from person")
        ids = [Id for Id, in cursor.fetchall()]
        if not person[0] in ids:
            cursor.execute("INSERT INTO person VALUES (?,?,?,?)", person)
        # El id de sesiones se incrementa cada vez que se insertan datos,
        # además se agrega la identificación del paciente.
        cursor.execute("SELECT count(sid) from session")
        session.insert(0, cursor.fetchone()[-1] + 1)
        session.insert(1, person[0])
        cursor.execute("INSERT INTO session VALUES (?,?,?,?,?,?)", session)
        # El id de parameters se incrementa cada vez que se ingresan datos.
        cursor.execute("SELECT count(cid) from parameters")
        n = cursor.fetchone()[-1]
        command = "INSERT INTO parameters VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        for idy, spt, angles in parameters:
            n += 1
            cursor.execute(
                command, (n, session[0], idy[0]) + spt + tuple(angles)
            )


def construct_select_stmt(column, table, fields):
    # La sintaxis sql para la selección de la columna c en la tabla t
    # donde las condiciones son verdaderas.
    base_stmt = "SELECT {c} FROM {t} WHERE ".format(c=column, t=table)
    # Se construyen las condiciones de selección según la lista que se
    # pasa como fields.
    conditions = []
    # La lista fields son pares columna (de la tabla t) valor que se
    # busca dentro de la columna col.
    for col, value in fields:
        if value:
            conditions.append("{k} = {v!r}".format(k=col, v=value))
    # Si no hay valores en fields, entonces la función devuelve None.
    if not conditions:
        return
    # Se construyen las condiciones para la claúsula WHERE del
    # base_stmt, a través del operador sql AND.
    full_conditions_stmt = ' AND '.join(conditions)
    return base_stmt + '(' + full_conditions_stmt + ')'


def search(database, person, session, platerality):
    # Se busca en la base de datos database a través de las listas de valores
    # para cada una de las tablas.
    sid_from_person, sid_from_session = None, None
    with sqlite3.connect(database, detect_types=1) as conn:
        cur = conn.cursor()
        if any(person):
            person_fields = zip(('fullname', 'age', 'dx'), person)
            # Se selecciona de la tabla personas las id (pid) de las personas
            # que cumplen con los valores que se pide en la lista person.
            cur.execute(construct_select_stmt('pid', 'person', person_fields))
            pids = [str(pid) for pid, in cur.fetchall()]
            # Ahora se seleccionan de la tabla sesiones las pid.
            if pids:
                pids_fields = zip(('personid',), pids)
                cur.execute(
                    construct_select_stmt('sid', 'session', pids_fields)
                    )
                sid_from_person = {sid for sid, in cur.fetchall()}

        if any(session):
            session_fields = zip(('assistance', 'test'), session)
            # Se selecciona de la tabla sesiones las id (sid) de las sesiones
            # que cumplen con los valores que se piden en la lista session.
            cur.execute(
                construct_select_stmt('sid', 'session', session_fields)
                )
            sid_from_session = {sid for sid, in cur.fetchall()}

        if sid_from_person and sid_from_session:
            # Si se pasaron las dos listas con al menos un valor en cada una,
            # entonces se aceptan los valores en común (intersect).
            sids = tuple(sid_from_person.intersection(sid_from_session))

        elif sid_from_person:
            sids = tuple(sid_from_person)

        elif sid_from_session:
            sids = tuple(sid_from_session)

        # Si no se consiguieron identificaciones en la base de datos entonces
        # se devuelve None.
        else:
            return None

        parameters = []
        for sid in sids:
            cur.execute('SELECT * FROM parameters WHERE sessionid = ?', (sid,))
            for row in cur.fetchall():
                idy = row[:3][::-1]
                spt = row[3:9]
                angles = np.array(row[9:])
                # NOTE: Se modifica el identificador de ciclos. En el motor de
                # cinemática el identificador tenia los componentes :
                # lateralidad, tipo de stream, caminata y ciclo.
                # Ahora los componentes del identificador son:
                # lateralidad, sesion, y ciclo (referido al orden en que se
                # introdujeron en la base de datos).
                parameters.append(('{0}SS{1}CY{2}'.format(*idy), spt, angles))
    return parameters
