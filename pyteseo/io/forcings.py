"""Input and Output functionality for specific TESEO file formats
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pyteseo.defaults import DEF_FILES, DEF_PATTERNS, DEF_VARS
from pyteseo.io.utils import (
    _check_cte_dt,
    _check_lonlat_range,
    _check_varnames,
    _check_n_vars,
    _check_lonlat_soting,
)


# 2. FORCINGS
def read_cte_forcing(path: str, forcing_type: str, dt: float) -> pd.DataFrame:

    file_column_names = DEF_VARS[forcing_type]["vars"]

    path = Path(path)
    df = pd.read_csv(path, delimiter="\s+", header=None)
    _check_n_vars(df, file_column_names)
    df.columns = file_column_names

    df.insert(0, "time", df.index.values * dt)

    # FIXME
    if forcing_type in ["currents", "winds"]:
        df = df.rename(columns={"u": "mod", "v": "dir"})

    return df


def read_2d_forcing(path: str, forcing_type: str) -> pd.DataFrame:
    """Read TESEO 2d forcings from list files

    Args:
        path (str | PosixPath | WindowsPath): path to TESEO lstcurr_UVW.pre, lstwinds.pre or lstwaves.pre
        varnames (list): list of column varnames in the file

    Returns:
        pd.DataFrame: Table data of currents, winds, or waves [time, +varnames].
    """
    coordnames = DEF_VARS[forcing_type]["coords"]
    varnames = DEF_VARS[forcing_type]["vars"]
    file_column_names = (coordnames + varnames)[1:]

    path = Path(path)
    files = read_list_file(path)

    df_list = []
    for file in files:
        df = pd.read_csv(file, delimiter="\s+", header=None)
        _check_n_vars(df, file_column_names)
        df.columns = file_column_names
        _check_lonlat_range(df, file_column_names)
        _check_lonlat_soting(df)

        df.insert(loc=0, column="time", value=float(file.stem[-4:-1]))
        df_list.append(df)

    n_rows = list(set([len(df.index) for df in df_list]))
    if len(n_rows) != 1:
        raise ValueError("Number of lines in each file are not equal!")

    df = pd.concat(df_list)
    _check_cte_dt(df)

    return df


def read_list_file(path):
    path = Path(path)
    with open(path, "r") as f:
        files = [Path(path.parent, line.rstrip()) for line in f]
    return files


def write_cte_forcing(
    df: pd.DataFrame, dir_path: str, forcing_type: str, nan_value=0
) -> None:
    lst_filename = DEF_FILES[forcing_type]
    coordnames = DEF_VARS[forcing_type]["coords"][0]
    varnames = DEF_VARS[forcing_type]["vars"]
    # FIXME - Use always UV
    if forcing_type in ["currents", "winds"]:
        varnames = ["mod", "dir"]
    path = Path(dir_path, lst_filename)

    df = df.sort_values([coordnames])
    _check_cte_dt(df)

    df.to_csv(
        path,
        sep="\t",
        columns=varnames,
        header=False,
        index=False,
        float_format="%.8e",
        na_rep=nan_value,
    )


def write_2d_foring(
    df: pd.DataFrame, dir_path: str, forcing_type: str, nan_value: int = 0
) -> None:

    lst_filename = DEF_FILES[forcing_type]
    file_pattern = DEF_PATTERNS[forcing_type]
    varnames = DEF_VARS[forcing_type]["vars"]
    coordnames = DEF_VARS[forcing_type]["coords"]
    path = Path(dir_path, lst_filename)

    df = df.sort_values(coordnames)

    _check_varnames(df, varnames + coordnames)
    _check_lonlat_range(df, coordnames)
    _check_cte_dt(df)

    grouped = df.groupby(coordnames[0])
    for time, group in grouped:
        with open(path, "a") as f:
            f.write(f"{file_pattern}\n".replace("*", f"{int(time):03d}"))

        path_currents = Path(path.parent, file_pattern.replace("*", f"{int(time):03d}"))
        group.to_csv(
            path_currents,
            sep="\t",
            columns=coordnames[1:] + varnames,
            header=False,
            index=False,
            float_format="%.8e",
            na_rep=nan_value,
        )


def write_null_forcing(dir_path, forcing_type):

    columns = [DEF_VARS[forcing_type]["coords"][0]] + DEF_VARS[forcing_type]["vars"]
    df = pd.DataFrame([{var: 0 for var in columns}])

    # FIXME
    if forcing_type in ["currents", "winds"]:
        df = df.rename(columns={"u": "mod", "v": "dir"})

    write_cte_forcing(df, dir_path, forcing_type, 1)
