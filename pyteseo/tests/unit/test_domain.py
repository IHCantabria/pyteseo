from pathlib import Path
from shutil import rmtree

import pandas as pd
import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.io.domain import (
    _split_polygons,
    read_coastline,
    read_grid,
    write_coastline,
    write_grid,
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
    "file, error",
    [
        ("grid.dat", None),
        ("not_existent_file.dat", "not_exist"),
        ("grid_error_var.dat", "bad_format"),
    ],
)
def test_read_grid(file, error):

    path = Path(data_path, file)

    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            df = read_grid(path, nan_value=-9999)
    elif error == "bad_format":
        with pytest.raises(ValueError):
            df = read_grid(path, nan_value=-9999)
    else:
        df = read_grid(path, nan_value=-9999)
        assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "error",
    [(None), ("df_n_var"), ("df_varnames"), ("lonlat_range"), ("sorting")],
)
def test_write_grid(error, setup_teardown):

    grid_path = Path(data_path, "grid.dat")
    output_path = Path(tmp_path, "test_grid.dat")

    df = read_grid(path=grid_path, nan_value=-9999)

    if error == "df_n_var":
        df["var"] = 123
        with pytest.raises(ValueError):
            write_grid(df=df, path=output_path, nan_value=-999)

    elif error == "df_varnames":
        df = df.rename(columns={"lon": "longitude"})
        with pytest.raises(ValueError):
            write_grid(df=df, path=output_path, nan_value=-999)

    elif error == "lonlat_range":
        df["lon"][0] = 360
        with pytest.raises(ValueError):
            write_grid(df=df, path=output_path, nan_value=-999)

    elif error == "sorting":
        df["lat"][0] == 90
        df["lat"][1] == 89

        write_grid(df=df, path=output_path, nan_value=-999)
        newdf = read_grid(path=output_path)
        output_path.unlink()
        output_path.parent.rmdir()
        assert all(newdf.get(["lon", "lat"]) == df.get(["lon", "lat"])) and all(
            df[df.get("depth").notna()] == newdf[newdf.get("depth").notna()]
        )

    else:
        write_grid(df=df, path=output_path, nan_value=-999)
        newdf = read_grid(path=output_path)
        output_path.unlink()
        output_path.parent.rmdir()
        assert all(newdf.get(["lon", "lat"]) == df.get(["lon", "lat"])) and all(
            df[df.get("depth").notna()] == newdf[newdf.get("depth").notna()]
        )


@pytest.mark.parametrize(
    "filename", [("coastline.dat"), ("coastline_othernanformat.dat")]
)
def test_split_polygons(filename):

    coastline_path = Path(data_path, filename)
    df = pd.read_csv(coastline_path, delimiter="\s+", header=None)

    coastline_df = _split_polygons(df)

    assert isinstance(coastline_df, pd.DataFrame)
    assert coastline_df.index.unique(0).values.max() == 4
    assert not coastline_df.empty


@pytest.mark.parametrize(
    "file, error",
    [
        ("coastline.dat", None),
        ("not_existent_file.dat", "not_exist"),
        ("coastline_error_range.dat", "bad_format"),
        ("grid.dat", "bad_format"),
    ],
)
def test_read_coastline(file, error):

    path = Path(data_path, file)

    if error == "not_exist":
        with pytest.raises(FileNotFoundError):
            df = read_coastline(path)
    elif error == "bad_format":
        with pytest.raises(ValueError):
            df = read_coastline(path)
    else:
        df = read_coastline(path)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "lon" in df.columns
        assert "lat" in df.columns
        assert "polygon" in df.index.names
        assert "point" in df.index.names
        assert df.index.unique(0).values.max() == 4


@pytest.mark.parametrize(
    "error", [(None), ("df_n_var"), ("df_varnames"), ("lonlat_range")]
)
def test_write_coastline(error, setup_teardown):

    coastline_path = Path(data_path, "coastline.dat")
    output_path = Path(tmp_path, "test_coastline.dat")

    df = read_coastline(path=coastline_path)

    if error == "df_n_var":
        df["var"] = 123
        with pytest.raises(ValueError):
            write_coastline(df=df, path=output_path)

    elif error == "df_varnames":
        df = df.rename(columns={"lon": "longitude"})
        with pytest.raises(ValueError):
            write_coastline(df=df, path=output_path)

    elif error == "lonlat_range":
        df.loc[:, ("lon")].values[0] = 360
        with pytest.raises(ValueError):
            write_coastline(df=df, path=output_path)

    else:
        write_coastline(df=df, path=output_path)
        newdf = read_coastline(path=output_path)

        assert all(newdf.get(["lon", "lat"]) == df.get(["lon", "lat"]))
