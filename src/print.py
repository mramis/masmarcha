#!/usr/bin/env python3

from configparser import ConfigParser
from json import load

import numpy as np

from engine import Engine
from representation import joint_plot, cycler_plot
from kinematics import resize_angles_sample

if __name__ == '__main__':
    config = ConfigParser()
    config.read('/home/mariano/masmarcha/masmarcha.ini')
    schema = load(open(config.get('paths', 'schema')))

    engine = Engine(config, schema)
    engine.load_session()
    # engine.plot_session()

    angles_list = []
    parameters_list = []
    angles_labels = []
    for c in engine.cycles:
        params = c.calculate_parameters(schema, config)
        idd, spat, angles = params
        angles_list.append(resize_angles_sample(angles, 101))
        angles_labels.append(idd)
        # switch_phase.append((c.cycle[1] - c.cycle[0]) / (c.cycle[2] - c.cycle[0]) * 100)
        # parameters_list.append(calculate_spatiotemporal_parameters(c.cycle, c.markers, engine.fps, engine.pixelscale))
    angles = np.array(angles_list)
    for i, joint in enumerate(('cadera', 'rodilla', 'tobillo')):
        joint_plot(joint, angles[:, i, :], config, angles_labels)

    # CYCLER --
    for w in engine.walks:
        cycler_plot(w, config)
