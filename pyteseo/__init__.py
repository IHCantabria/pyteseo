"""Python package developed to simplify and facilitate the setup and processing of TESEO simulations (TESEO is a lagrangian numerical model developed by IHCantabria)
"""

__version__ = "0.0.5"

import json
from pathlib import Path


with open(Path("pyteseo", "default_names.json"), "r") as f:
    data = f.read()
DEF_NAMES = json.loads(data)
