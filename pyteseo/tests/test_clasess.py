from pathlib import Path
from shutil import rmtree

import pytest
from pyteseo.classes import TeseoGrid, TeseoCurrents, TeseoWinds, TeseoWaves
from pyteseo.defaults import DEF_FILES
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
    "path, dt_cte",
    [
        (Path(data_path, DEF_FILES["currents"]), None),
        (Path(data_path, "lstcurr_UVW_cte.pre"), 1),
    ],
)
def test_TeseoCurrents(path, dt_cte):

    currents = TeseoCurrents(path, dt_cte)
    assert isinstance(currents.path, str)
    assert currents.dt == 1
    assert currents.nt == 4
    if dt_cte:
        assert "time" in currents.load.keys()
        assert "mod" in currents.load.keys()
        assert "dir" in currents.load.keys()
    else:
        assert "time" in currents.load.keys()
        assert "lon" in currents.load.keys()
        assert "lat" in currents.load.keys()
        assert "u" in currents.load.keys()
        assert "v" in currents.load.keys()


@pytest.mark.parametrize(
    "path, dt_cte",
    [
        (Path(data_path, DEF_FILES["winds"]), None),
        (Path(data_path, "lstwinds_cte.pre"), 1),
    ],
)
def test_TeseoWinds(path, dt_cte):

    winds = TeseoWinds(path, dt_cte)
    assert isinstance(winds.path, str)
    assert winds.dt == 1
    assert winds.nt == 4
    if dt_cte:
        assert "time" in winds.load.keys()
        assert "mod" in winds.load.keys()
        assert "dir" in winds.load.keys()
    else:
        assert "time" in winds.load.keys()
        assert "lon" in winds.load.keys()
        assert "lat" in winds.load.keys()
        assert "u" in winds.load.keys()
        assert "v" in winds.load.keys()


@pytest.mark.parametrize(
    "path, dt_cte",
    [
        (Path(data_path, DEF_FILES["waves"]), None),
        (Path(data_path, "lstwaves_cte.pre"), 1),
    ],
)
def test_TeseoWaves(path, dt_cte):

    winds = TeseoWaves(path, dt_cte)
    assert isinstance(winds.path, str)
    assert winds.dt == 1
    assert winds.nt == 4
    if dt_cte:
        assert "time" in winds.load.keys()
        assert "hs" in winds.load.keys()
        assert "dir" in winds.load.keys()
        assert "tp" in winds.load.keys()
    else:
        assert "time" in winds.load.keys()
        assert "lon" in winds.load.keys()
        assert "lat" in winds.load.keys()
        assert "hs" in winds.load.keys()
        assert "dir" in winds.load.keys()
        assert "tp" in winds.load.keys()
