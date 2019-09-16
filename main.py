#!/usr/bin/env python3
# coding: utf-8


import logging
from gui.masmarchaapp import MasMarchaApp

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

app = MasMarchaApp()
app.run()
