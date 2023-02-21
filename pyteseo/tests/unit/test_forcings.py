from pathlib import Path
from shutil import rmtree

import pandas as pd
import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.io.forcings import (
    read_2d_forcing,
    write_2d_forcing,
    read_cte_forcing,
    write_cte_forcing,
    write_null_forcing,
)


data_path = Path(__file__).parent.parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "file, varnames, error",
    [
        ("lstcurr_UVW.pre", "currents", None),
        ("lstwinds.pre", "winds", None),
        ("lstwaves.pre", "waves", None),
        ("lstcurr_UVW_not_exists.pre", "currents", "not_exist"),
    ],
)
def test_read_2d_forcings(file, varnames, error):

    path = Path(data_path, file)

    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            df = read_2d_forcing(path, varnames)
    elif error in ["sort", "range", "var"]:
        with pytest.raises(ValueError):
            df = read_2d_forcing(path, varnames)
    else:
        df = read_2d_forcing(path, varnames)
        assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "type, in_file, out_file",
    [
        ("currents", "lstcurr_UVW.pre", "currents_001h.txt"),
        ("winds", "lstwinds.pre", "winds_001h.txt"),
        ("waves", "lstwaves.pre", "waves_001h.txt"),
    ],
)
def test_write_2d_forcings(type, in_file, out_file, setup_teardown):
    df = read_2d_forcing(Path(data_path, in_file), type)

    write_2d_forcing(df=df, dir_path=tmp_path, forcing_type=type)
    assert Path(tmp_path, in_file).exists()
    assert Path(tmp_path, out_file).exists()


@pytest.mark.parametrize(
    "type, in_file, dt",
    [
        ("currents", "lstcurr_UVW_cte.pre", 1),
        ("winds", "lstwinds_cte.pre", 1),
        ("waves", "lstwaves_cte.pre", 1),
    ],
)
def test_read_cte_forcings(in_file, type, dt, setup_teardown):

    df = read_cte_forcing(Path(data_path, in_file), type, dt)
    assert "time" in df.keys()
    if type in ["currents", "winds"]:
        assert "mod" in df.keys()
        assert "dir" in df.keys()
    elif type == "waves":
        assert "hs" in df.keys()
        assert "dir" in df.keys()
        assert "tp" in df.keys()


@pytest.mark.parametrize(
    "type, in_file, out_file, dt",
    [
        ("currents", "lstcurr_UVW_cte.pre", "lstcurr_UVW.pre", 1),
        ("winds", "lstwinds_cte.pre", "lstwinds.pre", 1),
        ("waves", "lstwaves_cte.pre", "lstwaves.pre", 1),
    ],
)
def test_write_cte_forcings(type, in_file, out_file, dt, setup_teardown):
    df = read_cte_forcing(Path(data_path, in_file), type, dt)
    write_cte_forcing(df, tmp_path, type)

    assert Path(tmp_path, out_file).exists()


@pytest.mark.parametrize(
    "type, out_file",
    [
        ("currents", "lstcurr_UVW.pre"),
        ("winds", "lstwinds.pre"),
        ("waves", "lstwaves.pre"),
    ],
)
def test_write_null_forcing(type, out_file, setup_teardown):
    write_null_forcing(tmp_path, type)

    assert Path(tmp_path, out_file).exists()
    df = read_cte_forcing(Path(tmp_path, out_file), type, 1)
    assert len(df.index) == 1
    assert (df.values == 0).all()
