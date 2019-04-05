

import logging
from src.masmarchaapp import MasMarchaApp

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

app = MasMarchaApp()
app.run()
