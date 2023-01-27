from pathlib import Path
from shutil import rmtree

import pandas as pd

import pytest
from pyteseo.classes import TeseoGrid, TeseoCurrents, TeseoWinds
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


# def test_TeseoWrapper():

#     job = TeseoWrapper(input_dir=data_path)
#     assert job.grid is not None
#     assert job.coastline is None
#     assert job.currents is not None
#     assert job.winds is not None
#     # assert job.waves is None
#     # assert job.currents_depthavg is None


@pytest.mark.parametrize(
    "path, error",
    [
        (Path(data_path, "grid.dat"), None),
        (Path(data_path, "not_exist.file"), "not_exist"),
    ],
)
def test_TeseoGrid(path, error):
    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            grid = TeseoGrid(path)
    else:
        grid = TeseoGrid(path)
        assert isinstance(grid.path, str)
        assert grid.dx == pytest.approx(0.00050, abs=0.00001)
        assert grid.dy == pytest.approx(0.00050, abs=0.00001)
        assert grid.nx == 238
        assert grid.ny == 267


@pytest.mark.parametrize(
    "path, error",
    [
        (Path(data_path, "lstcurr_UVW.pre"), None),
        (Path(data_path, "not_exist.file"), "not_exist"),
    ],
)
def test_TeseoCurrents(path, error):
    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            currents = TeseoCurrents(path)
    else:
        currents = TeseoCurrents(path)
        assert isinstance(currents.path, str)
        assert currents.dx == 0.125
        assert currents.dy == 0.125
        assert currents.dt == 1
        assert currents.nx == 4
        assert currents.ny == 3
        assert currents.nt == 4


@pytest.mark.parametrize(
    "path, error",
    [
        (Path(data_path, "lstwinds.pre"), None),
        (Path(data_path, "not_exist.file"), "not_exist"),
    ],
)
def test_TeseoWinds(path, error):
    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            winds = TeseoWinds(path)
    else:
        winds = TeseoWinds(path)
        assert isinstance(winds.path, str)
        assert winds.dx == 0.125
        assert winds.dy == 0.125
        assert winds.dt == 1
        assert winds.nx == 4
        assert winds.ny == 3
        assert winds.nt == 4
        assert isinstance(winds.load, pd.DataFrame)
