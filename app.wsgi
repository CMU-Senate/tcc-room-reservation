#!/usr/bin/env python3

import sys
from pathlib import Path

root = Path('/var/www/tcc-room-reservation')

activate_this = str(root / 'venv/bin/activate_this.py')
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, str(root))

from app import app as application
