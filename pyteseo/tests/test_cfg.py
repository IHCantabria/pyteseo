from pathlib import Path
from shutil import rmtree
from datetime import datetime, timedelta
from pyteseo.io.cfg import (
    set_time,
    set_climate_vars,
    set_instantaneous_release,
    set_continuous_release,
    set_simulation_parameters,
)


import pytest

from pyteseo.__init__ import __version__ as v


data_path = Path(__file__).parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


def test_set_time():
    time_cfg = set_time(
        initial_datetime=datetime(2023, 1, 1, 0, 0, 0),
        duration=timedelta(hours=12),
        timestep=timedelta(seconds=60),
    )

    assert time_cfg["initial_datetime"] == datetime(2023, 1, 1, 0, 0, 0).isoformat()
    assert isinstance(time_cfg["duration"], float)
    assert isinstance(time_cfg["timestep"], float)


def test_set_climate_vars():
    climate_vars = set_climate_vars(
        air_temp=15,
        sea_temp=22,
        sea_dens=1024,
    )
    assert climate_vars["seawater_cinematic_viscosity"] == 1.004e-6
    assert climate_vars["seawater_temperature"] == 22


def test_set_instantaneous_release():
    release_config = set_instantaneous_release(n_points=3)

    assert release_config["type"] == "instantaneous"
    assert release_config["parameters"]["n_points"] == 3


def test_set_continuous_release():
    release_config = set_continuous_release(
        n_points=3,
        release_duration=timedelta(hours=3),
        subspill_timestep=timedelta(minutes=5),
    )

    assert release_config["type"] == "continuous"
    assert release_config["parameters"]["release_duration"] == 3
    assert release_config["parameters"]["subspill_timestep"] == 300


def test_set_simulation_parameters():
    simulation_parameters = set_simulation_parameters()
    assert simulation_parameters["simulation_type"] == "2d"
    assert simulation_parameters["motion_type"] == "forwards"
    assert simulation_parameters["weathering_type"] == "drifter"
