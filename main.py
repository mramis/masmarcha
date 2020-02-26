#!/usr/bin/env python3
# coding: utf-8


import logging
from gui.masmarchaapp import MasMarchaApp

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

app = MasMarchaApp()
app.run()
