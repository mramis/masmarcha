#!/usr/bin/env python3

from configparser import ConfigParser
from json import load

from engine import VideoEngine, KinoveaTrayectoriesEngine

from preview import path

if __name__ == '__main__':
    config = ConfigParser()
    config.read('/home/mariano/masmarcha/masmarcha.ini')

    schema = load(open(config.get('paths', 'schema')))

    print('Inicia Motor.')
    engine = VideoEngine(config, schema)

    print('Inicia búsqueda de caminatas')
    engine.search_for_walks(path)
    print('Listo')

    print('Inicia búsqueda de ciclos')
    engine.explore_walks()
    print('Listo')

    engine.dump_session()
    print('Datos de session almacenados')
