from pathlib import Path
from shutil import rmtree

import pandas as pd
import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.io.forcings import (
    write_currents,
    write_winds,
    read_2d_forcings,
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


@pytest.mark.parametrize(
    "file, varnames, error",
    [
        ("lstcurr_UVW.pre", ["lon", "lat", "u", "v"], None),
        ("lstwinds.pre", ["lon", "lat", "u", "v"], None),
        # ("lstwaves.pre", ["lon", "lat", "hs", "tp", "dir"], None),
        ("lstcurr_UVW_not_exists.pre", ["lon", "lat", "u", "v"], "not_exist"),
        ("lstcurr_UVW_error_sort.pre", ["lon", "lat", "u", "v"], "sort"),
        ("lstcurr_UVW_error_range.pre", ["lon", "lat", "u", "v"], "range"),
        ("lstcurr_UVW_error_var.pre", ["lon", "lat", "u", "v"], "var"),
    ],
)
def test_read_2d_forcings(file, varnames, error):

    path = Path(data_path, file)

    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            df = read_2d_forcings(path, varnames)
    elif error in ["sort", "range", "var"]:
        with pytest.raises(ValueError):
            df = read_2d_forcings(path, varnames)
    else:
        df = read_2d_forcings(path, varnames)
        assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize("error", [(None), ("df_varnames"), ("lonlat_range")])
def test_write_currents(error, setup_teardown):

    currents_path = Path(data_path, "lstcurr_UVW.pre")
    df = read_2d_forcings(currents_path, ["lon", "lat", "u", "v"])

    if error == "df_varnames":
        df = df.rename(columns={"lon": "longitude"})
        with pytest.raises(ValueError):
            write_currents(df, tmp_path)

    elif error == "lonlat_range":
        df.loc[:, ("lon")].values[0] = 360
        with pytest.raises(ValueError):
            write_currents(df, tmp_path)

    else:
        write_currents(df, tmp_path)
        assert Path(tmp_path, "lstcurr_UVW.pre").exists()


@pytest.mark.parametrize("error", [(None), ("df_varnames"), ("lonlat_range")])
def test_write_winds(error, setup_teardown):

    winds_path = Path(data_path, "lstwinds.pre")
    df = read_2d_forcings(winds_path, ["lon", "lat", "u", "v"])

    if error == "df_varnames":
        df = df.rename(columns={"lon": "longitude"})
        with pytest.raises(ValueError):
            write_winds(df, tmp_path)

    elif error == "lonlat_range":
        df.loc[:, ("lon")].values[0] = 360
        with pytest.raises(ValueError):
            write_winds(df, tmp_path)

    else:
        write_winds(df, tmp_path)
        assert Path(tmp_path, "lstwinds.pre").exists()
