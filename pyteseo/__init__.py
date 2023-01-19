"""Python package developed to simplify and facilitate the setup and processing of TESEO simulations (TESEO is a lagrangian numerical model developed by IHCantabria)
"""

__version__ = "0.0.5"

import json
from pathlib import Path


with open(Path("pyteseo", "defaults.json"), "r") as f:
    data = f.read()
defaults = json.loads(data)

DEF_DIRS = defaults["dirs"]
DEF_FILES = defaults["files"]
DEF_VARS = defaults["vars"]
DEF_COORDS = defaults["coords"]
DEF_TESEO_RESULTS_MAP = defaults["teseo_results_map"]
