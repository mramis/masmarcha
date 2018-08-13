#!/usr/bin/env python3

from configparser import ConfigParser
from json import load

from video import play, draw_markers, draw_rois
from engine import VideoEngine

path = "/home/mariano/Descargas/VID_20180813_182041747.mp4"

if __name__ == '__main__':
    config = ConfigParser()
    config.read('/home/mariano/masmarcha/masmarcha.ini')
    schema = load(open(config.get('paths', 'schema')))
    extrapx = config.getint('engine', 'extrapixel')
    play(path, 0.0, draw_markers, markers=None, wichone=None)

    # play(path, 0.005, draw_rois, regions=None, schema=schema, extrapx=extrapx)
