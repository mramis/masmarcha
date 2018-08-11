#!/usr/bin/env python3

from configparser import ConfigParser
from json import load

import numpy as np

from engine import Engine
from kinematics import resize_angles_sample

if __name__ == '__main__':
    config = ConfigParser()
    config.read('/home/mariano/masmarcha/masmarcha.ini')
    schema = load(open(config.get('paths', 'schema')))

    engine = Engine(config, schema)
    engine.load_session()
    engine.plot_session(withlabels=True, withtext=True)
