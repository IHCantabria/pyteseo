from datetime import datetime, timedelta
from pathlib import Path
from shutil import rmtree

import pandas as pd
import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.io.cfg import (
    set_climate_vars,
    set_continuous_release,
    set_hns_table,
    set_instantaneous_release,
    set_processes,
    set_simulation_parameters,
    set_spill_points_cfg,
    set_spreading_config,
    set_time,
)

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


@pytest.mark.parametrize(
    "error",
    [
        (None),
        (["2d", "forwards", "invalid_keyword"]),
        (["2d", "invalid_keyword", "drifter"]),
        (["invalid_keyword", "backwards", "drifter"]),
    ],
)
def test_set_simulation_parameters(error):
    if error:
        with pytest.raises(ValueError):
            simulation_parameters = set_simulation_parameters(
                simulation_type=error[0],
                motion_type=error[1],
                weathering_type=error[2],
            )
    simulation_parameters = set_simulation_parameters()
    assert simulation_parameters["simulation_type"] == "2d"
    assert simulation_parameters["motion_type"] == "forwards"
    assert simulation_parameters["weathering_type"] == "drifter"


@pytest.mark.parametrize(
    "keyword, error",
    [
        ("adios2", None),
        ("invalid_keyword", "error"),
    ],
)
def test_set_spreading_config(keyword, error):
    if error:
        with pytest.raises(ValueError):
            spreading_cfg = set_spreading_config(
                spreading_type=keyword, duration=timedelta(hours=3)
            )
    else:
        spreading_cfg = set_spreading_config(
            spreading_type=keyword, duration=timedelta(hours=3)
        )
        assert spreading_cfg["spreading_duration"] == 3
        assert spreading_cfg["spreading_type"] == "adios2"


def test_set_processes():
    processes = set_processes(
        spreading=True,
        evaporation=True,
        emulsification=True,
        vertical_dispersion=True,
        disolution=True,
        volatilization=True,
        sedimentation=True,
        biodegradation=True,
    )
    assert all([v for k, v in processes.items()])


def test_set_hns_table():
    hns_table = set_hns_table(n_spill_points=3, suspended_solids=[20, 15, 20])
    assert hns_table == "1  20 -0.32  0\n2  15 -0.32  0\n3  20 -0.32  0"


def test_set_spill_point_cfg():
    spill_points_cfg = set_spill_points_cfg(
        n_spill_points=2,
        release_time=[timedelta(hours=1.5), timedelta(minutes=80)],
        lon=[-3.80, -3.79],
        lat=[43.44, 43.45],
    )

    assert isinstance(spill_points_cfg, pd.DataFrame)
    assert len(spill_points_cfg["thickness"]) == 2
