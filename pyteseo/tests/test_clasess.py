from pathlib import Path
from shutil import rmtree

import pytest
from pyteseo.classes import TeseoGrid, TeseoCurrents
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
    "path, error, dt_cte",
    [
        (Path(data_path, "lstcurr_UVW.pre"), None, None),
        (Path(data_path, "not_exist.file"), "not_exist", None),
        (Path(data_path, "lstcurr_UVW_cte.pre"), None, 1),
    ],
)
def test_TeseoCurrents(path, error, dt_cte):
    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            currents = TeseoCurrents(path, dt_cte)
    else:
        currents = TeseoCurrents(path, dt_cte)
        assert isinstance(currents.path, str)
        # assert currents.dx == 0.125
        # assert currents.dy == 0.125
        assert currents.dt == 1
        # assert currents.nx == 4
        # assert currents.ny == 3
        assert currents.nt == 4
