#!/usr/bin/env python3

from configparser import ConfigParser
from json import load
import os

import numpy as np

# from engine import Engine
# from database import *

config = ConfigParser()
config.read('/home/mariano/masmarcha/masmarcha.ini')
schema = load(open(config.get('paths', 'schema')))

# NOTE: Le falta cargar los datos en la base y copar el video en capturas

# engine = Engine(config, schema)
# engine.load_session()

if __name__ == '__main__':
    session = config.get('paths', 'session')
    session_files = os.listdir(session)
    for f in session_files:
        os.remove(os.path.join(session, f))

    splots = config.get('paths', 'splots')
    splots_files = os.listdir(splots)
    for f in splots_files:
        os.remove(os.path.join(splots, f))
