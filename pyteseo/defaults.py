import json

import numpy as np

from pathlib import Path
from datetime import timedelta


with open(Path(__file__).parent / "defaults.json", "r") as f:
    data = f.read()
defaults = json.loads(data)

DEF_DIRS = defaults["dirs"]
DEF_FILES = defaults["files"]
DEF_PATTERNS = defaults["patterns"]
DEF_VARS = defaults["varnames"]
DEF_COORDS = defaults["coords"]
DEF_TESEO_RESULTS_MAP = defaults["teseo_results_map"]

DEF_CFG_PARAMETERS = {
    "timestep": timedelta(minutes=1),
    "mode": "2d",
    "motion": "forward",
    "seawater_kinematic_viscosity": 1.004e-6,
    "seawater_temperature": 17,
    "seawater_density": 1025,
    "air_temperature": 15.5,
    "suspended_solid_concentration": 10,
    "water_slope": 0.0005,
    "release_type": "instantaneous",
    "release_duration": timedelta(hours=0),
    "release_timestep": timedelta(minutes=0),
}

DEF_SPILL_POINT_PARAMETERS = {
    "depth": np.nan,
    "initial_width": np.nan,
    "initial_length": np.nan,
    "volume": np.nan,
    "thickness": np.nan,
    "degradation_rate": np.nan,
    "wind_drag_alpha_coefficient": 0.2,
    "wind_drag_beta_coefficient": 0,
    "currents_factor": 1,
    "wave_factor": 1,
    "dispersion_flag": 1,
    "dispersion_coefficient": 2,
    "vertical_dispersion_coefficient": 0.01,
}

DEF_PROCESSES_PARAMETERS = {
    "drifter": {
        "spreading": False,
        "spreading_formulation": "adios2",
        "spreading_duration": timedelta(hours=0),
        "evaporation": False,
        "emulsification": False,
        "vertical_dispersion": False,
        "dissolution": False,
        "volatilization": False,
        "sedimentation": False,
        "biodegradation": False,
    },
    "oil": {
        "spreading": False,
        "spreading_formulation": "adios2",
        "spreading_duration": timedelta(hours=0),
        "evaporation": True,
        "emulsification": True,
        "vertical_dispersion": False,
        "dissolution": False,
        "volatilization": False,
        "sedimentation": False,
        "biodegradation": False,
    },
    "hns": {
        "spreading": True,
        "spreading_formulation": "mohid-hns",
        "spreading_duration": timedelta(hours=0),
        "evaporation": True,
        "emulsification": False,
        "vertical_dispersion": False,
        "dissolution": True,
        "volatilization": True,
        "sedimentation": False,
        "biodegradation": False,
    },
}
