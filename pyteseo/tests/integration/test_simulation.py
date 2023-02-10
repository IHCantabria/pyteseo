from pathlib import Path
from shutil import copyfile, rmtree
from datetime import datetime, timedelta

import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.classes import TeseoWrapper


data_path = Path(__file__).parent.parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


def test_drifter(setup_teardown):

    input_files = [
        "grid.dat",
        "coastline.dat",
        "lstcurr_UVW_cte.pre",
        "lstwinds_cte.pre",
        "lstwaves_cte.pre",
    ]
    input_files_dst = [
        "grid.dat",
        "coastline.dat",
        "lstcurr_UVW.pre",
        "lstwinds.pre",
        "lstwaves.pre",
    ]

    if not Path(tmp_path, "inputs").exists():
        Path(tmp_path, "inputs").mkdir()
    for src_file, dst_file in zip(input_files, input_files_dst):
        copyfile(Path(data_path, src_file), Path(tmp_path, "inputs", dst_file))

    job = TeseoWrapper(path=tmp_path)
    job.load_inputs()

    parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "drifter",
        "forcing_init_datetime": datetime(2023, 1, 1, 0, 0, 0),
        "duration": timedelta(hours=12),
        "timestep": timedelta(minutes=1),
        "spill_points": [
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=32),
                "lon": -3.49,
                "lat": 43.55,
                "initial_width": 1,
                "initial_length": 1,
            },
            {
                "release_time": datetime(2023, 1, 1, 0, 0, 0) + timedelta(minutes=12),
                "lon": -3.49,
                "lat": 43.55,
                "initial_width": 1,
                "initial_length": 1,
            },
        ],
    }
    job.setup(parameters)
    assert Path(job.cfg_path).exists()
    assert Path(job.run_path).exists()


def test_oil(setup_teardown):

    input_files = [
        "grid.dat",
        "coastline.dat",
        "lstcurr_UVW_cte.pre",
        "lstwinds_cte.pre",
        "lstwaves_cte.pre",
    ]
    input_files_dst = [
        "grid.dat",
        "coastline.dat",
        "lstcurr_UVW.pre",
        "lstwinds.pre",
        "lstwaves.pre",
    ]

    if not Path(tmp_path, "inputs").exists():
        Path(tmp_path, "inputs").mkdir()
    for src_file, dst_file in zip(input_files, input_files_dst):
        copyfile(Path(data_path, src_file), Path(tmp_path, "inputs", dst_file))

    job = TeseoWrapper(path=tmp_path)
    job.load_inputs()

    parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "oil",
        "forcing_init_datetime": datetime.utcnow().replace(
            minute=0, second=0, microsecond=0
        ),
        "duration": timedelta(hours=12),
        "timestep": timedelta(minutes=1),
        "spill_points": [
            {
                "release_time": datetime.utcnow().replace(second=0, microsecond=0),
                "lon": -3.49,
                "lat": 43.55,
                "initial_width": 1,
                "initial_length": 1,
                "substance": "oil_example",
                "mass": 1500,
                "thickness": 0.1,
            },
            {
                "release_time": datetime.utcnow().replace(
                    hour=3, minute=12, second=0, microsecond=0
                ),
                "lon": -3.49,
                "lat": 43.55,
                "initial_width": 1.5,
                "initial_length": 2.5,
                "substance": "oil_example",
                "mass": 3500,
                "thickness": 0.1,
            },
        ],
    }
    job.setup(parameters)
    assert Path(job.cfg_path).exists()
    assert Path(job.run_path).exists()


def test_hns(setup_teardown):

    input_files = [
        "grid.dat",
        "coastline.dat",
        "lstcurr_UVW_cte.pre",
        "lstwinds_cte.pre",
        "lstwaves_cte.pre",
    ]
    input_files_dst = [
        "grid.dat",
        "coastline.dat",
        "lstcurr_UVW.pre",
        "lstwinds.pre",
        "lstwaves.pre",
    ]

    if not Path(tmp_path, "inputs").exists():
        Path(tmp_path, "inputs").mkdir()
    for src_file, dst_file in zip(input_files, input_files_dst):
        copyfile(Path(data_path, src_file), Path(tmp_path, "inputs", dst_file))

    job = TeseoWrapper(path=tmp_path)
    job.load_inputs()

    parameters = {
        "mode": "2d",
        "motion": "forward",
        "substance_type": "hns",
        "forcing_init_datetime": datetime.utcnow().replace(
            minute=0, second=0, microsecond=0
        ),
        "duration": timedelta(hours=12),
        "timestep": timedelta(minutes=1),
        "spill_points": [
            {
                "release_time": datetime.utcnow().replace(second=0, microsecond=0),
                "lon": -3.49,
                "lat": 43.55,
                "initial_width": 1,
                "initial_length": 1,
                "substance": "hns_example",
                "mass": 1500,
                "thickness": 0.1,
            },
            {
                "release_time": datetime.utcnow().replace(
                    hour=3, minute=12, second=0, microsecond=0
                ),
                "lon": -3.49,
                "lat": 43.55,
                "initial_width": 1.5,
                "initial_length": 2.5,
                "substance": "hns_example",
                "mass": 3500,
                "thickness": 0.1,
            },
        ],
    }
    job.setup(parameters)
    assert Path(job.cfg_path).exists()
    assert Path(job.run_path).exists()
