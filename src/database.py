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


def create(filename):
    u"""."""
    # Este código se encarga de la creación de la base de datos y de las
    # tablas que contienen toda la información de la aplicación. Se realiza
    # por única vez cuando se corre el archivo setup.
    with sqlite3.connect(filename, detect_types=1) as conn:
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
    u"""."""
    with sqlite3.connect(database, detect_types=1) as conn:
        cur = conn.cursor()
        # La persona puede existir(id), por eso está en un try-except.
        try:
            cur.execute("insert into person values (?,?,?,?,?)", person)
        except sqlite3.IntegrityError:
            logging.info("person-id(%s) existe en %s" % (person[0], database))

        cur.execute("""
            insert into session(pid, day, assistance, test, note)
            values (?,?,?,?,?)""", (person[0], ) + session)

        insert_stmt = """
            insert into parameters(sid, lat, duration, stance, swing, stride,
            cadency, velocity, hip, knee, ankle)
            values (?,?,?,?,?,?,?,?,?,?,?)"""
        sid = cur.lastrowid
        for idy, spt, angles in parameters:
            cur.execute(insert_stmt, (sid, idy[0]) + spt + tuple(angles))


def search(database, name, lastname, age, dx, assistance, test):
    u"""."""
    # En este código se realiza una búsqueda (y extracción) de parámetros
    # basada en la sentencia SELECT sqlite. Esta sentencia contienen la
    # cláusula WHERE (condición).
    with sqlite3.connect(database, detect_types=1) as conn:
        cur = conn.cursor()
        # En el las líneas que siguen se construyen las condiciones de la
        # clausula WHERE para la tabla persona. La lista where_clause_cond
        # contiene las cadenas de texto que forman una condición según la
        # sintaxis sqlite3: "column = ?", la lista where_clause_values
        # contiene los valores que la función `sqlite3.cursor().execute`
        # reemplaza en los tokens "?" de las codiciones. Es importante que las
        # listas tengan el mismo número de componentes, es decir, un valor para
        # cada token "?".
        person_ids = []
        where_clause_cond = []
        where_clause_values = []
        if lastname:
            where_clause_cond.append('lastname = ?')
            where_clause_values.append(lastname)
        if name:
            where_clause_cond.append('name = ?')
            where_clause_values.append(name)
        if age:
            age = re.findall('[0-9]+', age)
            where_clause_cond.append('age >= ?')
            where_clause_values.append(min(age))
            where_clause_cond.append('age <= ?')
            where_clause_values.append(max(age))
        if dx:
            where_clause_cond.append('dx = ?')
            where_clause_values.append(dx)

        # Si la función recibió argumentos que están en la tabla personas,
        # se ensambla el argumento de la clausula WHERE. Cada condición de
        # la lista where_clause_cond se une a través del operador "AND" de
        # sql. Al final se obtiene la sentencia SELECT con las condiciones
        # requeridas para la búsqueda de pids en la tabla personas.
        # Estas pids luego se utilizan en la tabla sesiones para la búsqueda
        # de sids(identificador de sesiones)
        if where_clause_cond:
            where_args = ' AND '.join(where_clause_cond)
            select_stmt = "SELECT id FROM person WHERE (...)"
            cur.execute(select_stmt.replace('...', where_args),
                        where_clause_values)
            person_ids = [ID for ID, in cur.fetchall()]

        # En el las líneas que siguen se construyen las condiciones de la
        # clausula WHERE para la tabla sesiones. Se utiliza el mismo principio
        # para la construcción de las condiciones, aunque se hacen ligeramente
        # distintas.
        session_ids = []
        where_clause_cond = []
        where_clause_values = []
        # Si existen identificaciones de la tabla persona (pids), entonces el
        # operador que une las condiciones cambia por "OR".
        # Además si existen argumentos para la tabla sesiones, se debe crear
        # una condición por cada pid junto a cada columna de la tabla sesiones,
        # y estas separadas por un operador "AND".
        if person_ids:
            operator = " OR "
            if assistance and test:
                for pid in person_ids:
                    where_clause_cond.append(
                        'pid = ? AND assistance = ? AND test = ?'
                        )
                    where_clause_values.append((pid, assistance, test))
            elif assistance:
                for pid in person_ids:
                    where_clause_cond.append('pid = ? AND assistance = ?')
                    where_clause_values.append((pid, assistance))
            elif test:
                for pid in person_ids:
                    where_clause_cond.append('pid = ? AND test = ?')
                    where_clause_values.append((pid, test))
            else:
                for pid in person_ids:
                    where_clause_cond.append('pid = ?')
                    where_clause_values.append((pid,))
        else:
            # Si no existen argumentos que pertenencen a la tabla personas
            # entonces la construcción de las sentencias es la misma que para
            # la tabla personas.
            operator = ' AND '
            if assistance:
                where_clause_cond.append('assistance = ?')
                where_clause_values.append((assistance,))
            if test:
                where_clause_cond.append('test = ?')
                where_clause_values.append((test,))

        # Si se recibió algun argumento no nulo, entonces, se buscan y extraen
        # los sids (identificadores de session) que se utilizan para la
        # búsqueda de parámetros en esa tabla.
        if where_clause_cond:
            where_args = operator.join(where_clause_cond)
            select_stmt = "SELECT id FROM session WHERE (...)"
            # Acá el ensamblaje de las condiciones es ligeramente distinta
            # porque la lista where_clause_values no contiene cadenas si no,
            # tuples de cadenas, y lo que se hace es simplemente unir los
            # tuples en uno solo.
            where_clause_values = reduce(lambda a, b: a+b, where_clause_values)
            cur.execute(select_stmt.replace('...', where_args),
                        where_clause_values)
            session_ids = [ID for ID, in cur.fetchall()]

        # Finalmente si se pasa al menos algún argumento a la función, se
        # devuelven los parámetros donde se encontraron coincidencias.
        where_clause_cond = []
        if session_ids:
            for sid in session_ids:
                where_clause_cond.append('sid = ?')
            select_stmt = "SELECT * FROM parameters WHERE (...)"
            where_args = " OR ".join(where_clause_cond)
            cur.execute(select_stmt.replace('...', where_args), session_ids)
            return cur.fetchall()
