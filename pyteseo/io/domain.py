"""Input and Output functionality for specific TESEO file formats
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pyteseo.defaults import DEF_PATTERNS
from pyteseo.io.utils import _check_lonlat_range, _check_lonlat_soting


def read_grid(path: str, nan_value: float = -999) -> pd.DataFrame:
    """Read TESEO grid-file to pandas DataFrame

    Args:
        path (str): path to the grid-file
        nan_value (float, optional): value to set nans. Defaults to -999.

    Returns:
        pd.DataFrame: DataFrame with TESEO grid data [lon, lat, depth]
    """
    path = Path(path)
    df = pd.read_csv(path, delimiter="\s+", na_values=str(nan_value), header=None)

    if df.shape[1] != 3:
        raise ValueError(
            "TESEO grid-file should contains lon, lat and depth values only!"
        )

    df.columns = ["lon", "lat", "depth"]
    _check_lonlat_range(df)
    _check_lonlat_soting(df)

    return df


def read_coastline(path: str) -> pd.DataFrame:
    """Read TESEO coastline-file to pandas DataFrame

    Args:
        path (str | PosixPath): path to the coastline-file

    Returns:
        pd.DataFrame: DataFrame with TESEO coastline data [lon, lat]
    """
    path = Path(path)
    df = pd.read_csv(path, delimiter="\s+", header=None)
    if df.shape[1] != 2:
        raise ValueError("TESEO coastline-file should contains lon, lat values only!")

    df.columns = ["lon", "lat"]
    if (
        df.lon.max() >= 180
        or df.lon.min() <= -180
        or df.lat.max() >= 90
        or df.lat.min() <= -90
    ):
        raise ValueError(
            "lon and lat values in TESEO grid-file should be inside ranges lon[-180,180] and lat[-90,90]!"
        )

    return _split_polygons(df)


def _split_polygons(df: pd.DataFrame) -> pd.DataFrame:
    """Split DataFrame between nan values

    Args:
        df (pd.DataFrame): input DataFrame with nans

    Returns:
        pd.DataFrame: DataFrame with polygon and point number as indexes
    """
    splitted_dfs = []
    previous_i = count = 0
    n_nans = len(df[df.isna().any(axis=1)])

    for i in df[df.isna().any(axis=1)].index.values:
        count += 1
        if i == 0:
            continue
        if count == n_nans:
            splitted_dfs.append(df.iloc[previous_i:i])
            if i == df.iloc[[-1]].index.values:
                break
            else:
                splitted_dfs.append(df.iloc[i:])
        else:
            splitted_dfs.append(df.iloc[previous_i:i])
            previous_i = i

    if splitted_dfs[0].equals(df):
        print("WARNING - There is nothing to split in this DataFrame!")

    new_polygons = []
    for i, polygon in enumerate(splitted_dfs):
        polygon.loc[:, ("polygon")] = i + 1
        polygon.loc[:, ("point")] = polygon.index
        polygon = polygon.set_index(["polygon", "point"])
        new_polygons.append(polygon)

    return pd.concat(new_polygons)


def write_grid(df: pd.DataFrame, path: str, nan_value: float = -999) -> None:
    """Write TESEO grid-file

    Args:
        df (pd.DataFrame): DataFrame with columns 'lon', 'lat', 'depth' (lon:[-180,180], lat:[-90,90])
        path (str): path to the new grid-file
        nan_value (float, optional): define how will be writted nan values in the grid-file. Defaults to -999.
    """
    path = Path(path)

    if (
        "lon" not in df.keys().values
        or "lat" not in df.keys().values
        or "depth" not in df.keys().values
    ):
        raise ValueError(
            "variable names in DataFrame should be 'lon', 'lat' and 'depth'!"
        )

    if df.shape[1] != 3:
        raise ValueError(
            "DataFrame should contains column variables lon, lat and depth only!"
        )

    # FIXME - if [0,360] convert to [-180,180]
    if (
        df.lon.max() >= 180
        or df.lon.min() <= -180
        or df.lat.max() >= 90
        or df.lat.min() <= -90
    ):
        raise ValueError(
            "lon and lat values should be inside ranges lon[-180,180] and lat[-90,90]!"
        )

    df = df.sort_values(["lon", "lat"])
    df.to_csv(
        path,
        sep="\t",
        na_rep=nan_value,
        header=False,
        index=False,
        float_format="%.8e",
    )


def write_coastline(df: pd.DataFrame, path: str) -> None:
    """Write TESEO coastline and polygons files

    Args:
        df (pd.DataFrame): DataFrame with columns 'lon', 'lat' and polygons separated by nan lines (lon:[-180,180], lat:[-90,90])
        path (str): path to the new coastline-file
    """
    path = Path(path)

    if "lon" not in df.keys().values or "lat" not in df.keys().values:
        raise ValueError("variable names in DataFrame should be 'lon' and 'lat'!")

    if df.shape[1] != 2:
        raise ValueError("DataFrame should contains column variables lon and lat only!")

    # FIXME - if [0,360] convert to [-180,180]
    if (
        df.lon.max() >= 180
        or df.lon.min() <= -180
        or df.lat.max() >= 90
        or df.lat.min() <= -90
    ):
        raise ValueError(
            "lon and lat values should be inside ranges lon[-180,180] and lat[-90,90]!"
        )

    df.to_csv(
        path,
        sep="\t",
        header=False,
        index=False,
        float_format="%.8e",
        na_rep="NaN",
    )
    _write_polygons(df, path.parent)


def _write_polygons(
    df: pd.DataFrame,
    dir_path: str,
    filename_pattern: str = DEF_PATTERNS["polygons"],
) -> None:
    """Write polygons from a coastline DataFrame

    Args:
        df (pd.DataFrame): input coastline DataFrame
        dir_path (str): directory where polygon files will be created
        filename (str, optional): filename for polygon-files (numbering and extension will be added). Defaults to "coastline_polygon".
    """

    grouped = df.groupby("polygon")
    for polygon, group in grouped:
        path_polygon = Path(
            dir_path, f"{filename_pattern}".replace("*", f"{polygon:03d}")
        )
        group.to_csv(
            path_polygon,
            sep="\t",
            header=False,
            index=False,
            float_format="%.8e",
            na_rep="NaN",
        )
