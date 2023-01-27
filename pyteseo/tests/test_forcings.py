from pathlib import Path
from shutil import rmtree

import numpy as np
import pandas as pd
import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.io.forcings import (
    read_currents,
    read_winds,
    write_currents,
    write_winds,
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
    "file, error",
    [
        ("lstcurr_UVW.pre", None),
        ("lstcurr_UVW_not_exists.pre", "not_exist"),
        ("lstcurr_UVW_error_sort.pre", "sort"),
        ("lstcurr_UVW_error_range.pre", "range"),
        ("lstcurr_UVW_error_var.pre", "var"),
    ],
)
def test_read_currents(file, error):

    path = Path(data_path, file)

    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            df = read_currents(path)
    elif error in ["sort", "range", "var"]:
        with pytest.raises(ValueError):
            df = read_currents(path)
    else:
        df = read_currents(path)

        assert isinstance(df, pd.DataFrame)
        assert len(df["time"].unique()) == 4
        assert len(df["lon"].unique()) == 4
        assert len(df["lat"].unique()) == 3
        assert np.unique(np.diff(df["time"].unique()))[0] == 1


@pytest.mark.parametrize(
    "file, error",
    [
        ("lstwinds.pre", None),
        ("lstcurr_UVW_not_exists.pre", "not_exist"),
    ],
)
def test_read_winds(file, error):

    path = Path(data_path, file)

    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            df = read_winds(path)
    elif error in ["sort", "range", "var"]:
        with pytest.raises(ValueError):
            df = read_winds(path)
    else:
        df = read_winds(path)

        assert isinstance(df, pd.DataFrame)
        assert len(df["time"].unique()) == 4
        assert len(df["lon"].unique()) == 4
        assert len(df["lat"].unique()) == 3
        assert np.unique(np.diff(df["time"].unique()))[0] == 1


@pytest.mark.parametrize("error", [(None), ("df_varnames"), ("lonlat_range")])
def test_write_currents(error, setup_teardown):

    currents_path = Path(data_path, "lstcurr_UVW.pre")
    df = read_currents(currents_path)

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
    df = read_winds(winds_path)

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
