#!/usr/bin/env python3

from configparser import ConfigParser
from json import load

from video import play, draw_markers, draw_rois
from engine import VideoEngine

path = "/home/mariano/masmarcha/capturas/calb-dist-tomi.mp4"

if __name__ == '__main__':
    config = ConfigParser()
    config.read('/home/mariano/masmarcha/masmarcha.ini')
    schema = load(open(config.get('paths', 'schema')))

    engine = VideoEngine(config, schema)
    engine.set_distance_scale(path)
