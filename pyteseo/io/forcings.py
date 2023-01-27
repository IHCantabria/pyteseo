"""Input and Output functionality for specific TESEO file formats
"""
from __future__ import annotations

from pathlib import Path, PosixPath
from typing import Tuple

import pandas as pd
import numpy as np

from pyteseo.defaults import DEF_FILES, DEF_PATTERNS


# 2. FORCINGS
def read_currents(path: str | PosixPath) -> Tuple[pd.DataFrame, float, float, float]:
    """Read TESEO currents-files (2dh: [lon, lat, u, v])

    Args:
        path (str | PosixPath): path to TESEO lstcurr.pre file

    Returns:
        Tuple[pd.DataFrame, float, float, float]: DataFrame of currents, number of files (times), number of nodes, and dt in hours
    """
    path = Path(path)
    with open(path, "r") as f:
        files = [Path(path.parent, line.rstrip()) for line in f]

    df_list = _read_2dh_uv(files)

    n_rows = list(set([len(df.index) for df in df_list]))

    if len(n_rows) != 1:
        raise ValueError("Number of lines in each file are not equal!")

    df = pd.concat(df_list)
    dt_h = np.unique(np.diff(df["time"].unique()))
    if len(dt_h) != 1:
        raise ValueError("Forcing time steps are not constant!")

    return df


def read_winds(path: str | PosixPath) -> Tuple[pd.DataFrame, float, float, float]:
    """Read TESEO winds-files (2dh: [lon, lat, u, v])

    Args:
        path (str | PosixPath): path to TESEO lstwinds.pre file

    Returns:
        Tuple[pd.DataFrame, float, float, float]: DataFrame of winds, number of files (times), number of nodes, and dt in hours.
    """
    path = Path(path)
    with open(path, "r") as f:
        files = [Path(path.parent, line.rstrip()) for line in f]

    df_list = _read_2dh_uv(files)

    n_rows = list(set([len(df.index) for df in df_list]))

    if len(n_rows) != 1:
        raise ValueError("Number of lines in each file are not equal!")

    df = pd.concat(df_list)
    dt_h = np.unique(np.diff(df["time"].unique()))
    if len(dt_h) != 1:
        raise ValueError("Forcing time steps are not constant!")

    return df


def read_waves():
    pass


def write_currents(df: pd.DataFrame, dir_path: PosixPath | str) -> None:
    """Write TESEO currents-files from a DataFrame

    Args:
        df (pd.DataFrame): DataFrame containing columns "time", "lon", "lat", "u", and "v".
        dir_path (PosixPath | str): directory path where will be created the files "lstcurr_UVW.pre" and all the "currents_*.txt"
    """

    lst_filename = DEF_FILES["currents_list"]
    file_pattern = DEF_PATTERNS["currents_pattern"]
    path = Path(dir_path, lst_filename)

    _write_2dh_uv(df, path, file_pattern)


def write_winds(df: pd.DataFrame, dir_path: PosixPath | str) -> None:
    """Write TESEO winds-files from a DataFrame

    Args:
        df (pd.DataFrame): DataFrame containing columns "time", "lon", "lat", "u", and "v".
        dir_path (PosixPath | str): directory path where will be created the files "lstwinds.pre" and all the "winds_*.txt"
    """
    lst_filename = DEF_FILES["winds_list"]
    file_pattern = DEF_PATTERNS["winds_pattern"]
    path = Path(dir_path, lst_filename)

    _write_2dh_uv(df, path, file_pattern)


def _write_2dh_uv(
    df: pd.DataFrame, path: PosixPath | str, file_pattern: str, nan_value: int = 0
):
    """Write 2dh fields [time, lon, lat, u, v] to TESEO's format files

    Args:
        df (pd.DataFrame): DataFrame with the currents or fields
        path (PosixPath | str): path to the lstfile of teseo
        file_pattern (str): one of the following: ["winds_*.txt", "currents_*.txt", waves_*.txt]
        nan_value (int, optional): value for nan's in the file. Defaults to 0.
    """

    path = Path(path)

    # Check variable-names
    for varname in ["time", "lon", "lat", "u", "v"]:
        if varname not in df.keys():
            raise ValueError(f"{varname} not founded in the DataFrame")

    if (
        df.lon.max() >= 180
        or df.lon.min() <= -180
        or df.lat.max() >= 90
        or df.lat.min() <= -90
    ):
        raise ValueError(
            "lon and lat values should be inside ranges lon[-180,180] and lat[-90,90]!"
        )

    df = df.sort_values(["time", "lon", "lat"])

    if len(np.unique(np.diff(df["time"].unique()))) > 1:
        raise ValueError("Forcing time steps are not constant!")

    grouped = df.groupby("time")
    for time, group in grouped:
        with open(path, "a") as f:
            f.write(f"{file_pattern}\n".replace("*", f"{int(time):03d}"))

        path_currents = Path(path.parent, f"{file_pattern}_{int(time):03d}h.txt")
        group.to_csv(
            path_currents,
            sep="\t",
            columns=["lon", "lat", "u", "v"],
            header=False,
            index=False,
            float_format="%.8e",
            na_rep=nan_value,
        )


def write_zero_currents(dir_path):
    zero_df = pd.DataFrame({"time": [0], "u": [0], "v": [0]})
    write_cte_currents(df=zero_df, dir_path=dir_path)


def write_zero_winds(dir_path):
    zero_df = pd.DataFrame({"time": [0], "hs": [0], "tp": [0], "dir": [0]})
    _write_cte_waves(df=zero_df, dir_path=dir_path)


def write_cte_currents(df, dir_path, nan_value: int = 0) -> None:

    lst_filename = DEF_FILES["currents_list"]
    path = Path(dir_path, lst_filename)
    _write_cte_uv(df, nan_value, path)


def write_cte_winds(df, dir_path, nan_value: int = 0) -> None:

    lst_filename = DEF_FILES["winds_list"]
    path = Path(dir_path, lst_filename)
    _write_cte_uv(df, nan_value, path)


def _write_cte_uv(df, nan_value, path) -> None:

    _check_varnames(df, ["time", "u", "v"])
    path = Path(path)
    df = df.sort_values(["time"])
    _check_cte_dt(df)

    df.to_csv(
        path,
        sep="\t",
        columns=["u", "v"],
        header=False,
        index=False,
        float_format="%.8e",
        na_rep=nan_value,
    )


def _write_cte_moddir(df, nan_value, path) -> None:

    _check_varnames(df, ["time", "mod", "dir"])
    path = Path(path)
    df = df.sort_values(["time"])
    _check_cte_dt(df)

    df.to_csv(
        path,
        sep="\t",
        columns=["mod", "dir"],
        header=False,
        index=False,
        float_format="%.8e",
        na_rep=nan_value,
    )


def write_cte_waves(df, dir_path, nan_value: int = 0) -> None:

    lst_filename = DEF_FILES["waves_list"]
    path = Path(dir_path, lst_filename)
    _write_cte_waves(df, nan_value, path)


def _write_cte_waves(df, nan_value, path) -> None:

    _check_varnames(df, ["time", "hs", "tp", "dir"])
    path = Path(path)
    df = df.sort_values(["time"])
    _check_cte_dt(df)

    df.to_csv(
        path,
        sep="\t",
        columns=["hs", "tp", "dir"],
        header=False,
        index=False,
        float_format="%.8e",
        na_rep=nan_value,
    )


def _check_cte_dt(df):
    dt = np.unique(np.diff(df["time"].unique()))
    if len(dt) > 1:
        print(f"WARNING: Forcing time steps are not constant {dt}")


def _check_lonlat_range(df, vars):
    if "lon" in vars or "lat" in vars:
        if (
            df.lon.max() >= 180
            or df.lon.min() <= -180
            or df.lat.max() >= 90
            or df.lat.min() <= -90
        ):
            raise ValueError(
                "lon and lat values should be inside ranges lon[-180,180] and lat[-90,90]!"
            )


def _check_varnames(df, vars):
    for varname in vars:
        if varname not in df.keys():
            raise ValueError(f"{varname} not founded in the DataFrame")


def _read_2dh_uv(files: list[PosixPath | str]) -> list[pd.DataFrame]:
    """Read TESEO's 2dh velocity field files used for currents and winds. column format [lon, lat, u, v]

    Args:
        files (list[PosixPath | str]): paths where velocity field files are located. (sorted list)

    Returns:
        list[pd.DataFrame]: list of DataFrames for each file (adding time field)
    """
    df_list = []
    for file in files:
        df = pd.read_csv(file, delimiter="\s+", header=None)

        if df.shape[1] != 4:
            raise ValueError(
                "DataFrame should contains column variables lon, lat, u, and v only!"
            )

        df.columns = ["lon", "lat", "u", "v"]

        if (
            df.lon.max() >= 180
            or df.lon.min() <= -180
            or df.lat.max() >= 90
            or df.lat.min() <= -90
        ):
            raise ValueError(
                "lon and lat values should be inside ranges lon[-180,180] and lat[-90,90]!"
            )

        if not all(
            df.get(["lon", "lat"]) == df.sort_values(["lon", "lat"]).get(["lon", "lat"])
        ):
            raise ValueError("lon and lat values should be monotonic increasing!")

        df["mod"] = np.sqrt(df.u**2 + df.v**2)
        df.insert(loc=0, column="time", value=float(file.stem[-4:-1]))
        df_list.append(df)

    return df_list
