import json
from pathlib import Path


with open(Path(__file__).parent / "defaults.json", "r") as f:
    data = f.read()
defaults = json.loads(data)

DEF_DIRS = defaults["dirs"]
DEF_FILES = defaults["files"]
DEF_VARS = defaults["vars"]
DEF_COORDS = defaults["coords"]
DEF_TESEO_RESULTS_MAP = defaults["teseo_results_map"]
