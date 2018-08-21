#!/usr/bin/env python3

from configparser import ConfigParser
from json import load
import os

import numpy as np

from engine import Engine
import database

config = ConfigParser()
config.read('/home/mariano/masmarcha/masmarcha.ini')
schema = load(open(config.get('paths', 'schema')))

# NOTE: Le falta cargar los datos en la base y copar el video en capturas

engine = Engine(config, schema)
engine.load_session()

if __name__ == '__main__':
    db = config.get('paths', 'database')
    if not os.path.isfile(db):
        database.create(db)

    anws = input('ATENCION, se van a eliminar todos los datos (y/n?): ')
    if anws == 'y':

        session_data = load(open(config.get('paths', 'sessiondata')))
        kinematics = []
        for cycle in engine.cycles:
            __, spatemp, angles = cycle.calculate_parameters(schema, config)
            kinematics.append(((str(cycle.lat)[0],) + tuple(spatemp) + tuple(angles)))
        # agregamos los datos a la base sqlite
        database.insert(db, tuple(session_data['person']), tuple(session_data['session']), kinematics)

        # se remueven todos los datos y sus gráficas.
        session_path = config.get('paths', 'session')
        session_files = os.listdir(session_path)
        for f in session_files:
            os.remove(os.path.join(session_path, f))

        splots = config.get('paths', 'splots')
        splots_files = os.listdir(splots)
        for f in splots_files:
            os.remove(os.path.join(splots, f))
