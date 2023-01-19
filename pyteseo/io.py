"""Input and Output functionality for specific TESEO file formats
"""
from __future__ import annotations

from pathlib import Path, PosixPath, WindowsPath
from typing import Tuple

import pandas as pd
import numpy as np

from pyteseo.defaults import DEF_FILES, DEF_TESEO_RESULTS_MAP

# NOTE - Restricts what is documented by Sphinx (!!!)
# __all__ = [
#     "read_grid",
#     "read_coastline",
#     "write_grid",
#     "write_coastline",
#     "read_currents",
#     "read_winds",
#     "write_currents",
#     "write_winds",
#     "read_particles_results",
#     "read_properties_results",
#     "read_grids_results",
# ]


# 1. DOMAIN
def read_grid(
    path: str | PosixPath | WindowsPath, nan_value: int | float = -999
) -> pd.DataFrame:
    """Read TESEO grid-file to pandas DataFrame

    Args:
        path (str | PosixPath): path to the grid-file
        nan_value (float | int, optional): value to set nans. Defaults to -999.

    Returns:
        pd.DataFrame: DataFrame with TESEO grid data [lon, lat, depth]
    """

    df = pd.read_csv(path, delimiter="\s+", na_values=str(nan_value), header=None)

    if df.shape[1] != 3:
        raise ValueError(
            "TESEO grid-file should contains lon, lat and depth values only!"
        )

    df.columns = ["lon", "lat", "depth"]
    if (
        df.lon.max() >= 180
        or df.lon.min() <= -180
        or df.lon.max() >= 90
        or df.lon.min() <= -90
    ):
        raise ValueError(
            "lon and lat values in TESEO grid-file should be inside ranges lon[-180,180] and lat[-90,90]!"
        )

    if not all(
        df.get(["lon", "lat"]) == df.sort_values(["lon", "lat"]).get(["lon", "lat"])
    ):
        raise ValueError(
            "lon and lat values in TESEO grid-file should be monotonic increasing!"
        )
    return df


def read_coastline(path: str | PosixPath) -> pd.DataFrame:
    """Read TESEO coastline-file to pandas DataFrame

    Args:
        path (str | PosixPath): path to the coastline-file

    Returns:
        pd.DataFrame: DataFrame with TESEO coastline data [lon, lat]
    """
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


def write_grid(
    df: pd.DataFrame, path: str | PosixPath, nan_value: int | float = -999
) -> None:
    """Write TESEO grid-file

    Args:
        df (pd.DataFrame): DataFrame with columns 'lon', 'lat', 'depth' (lon:[-180,180], lat:[-90,90])
        path (str | PosixPath): path to the new grid-file
        nan_value (int | float, optional): define how will be writted nan values in the grid-file. Defaults to -999.
    """

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
        df = df.sort_values(["lon", "lat"])

    df.to_csv(
        path,
        sep="\t",
        na_rep=nan_value,
        header=False,
        index=False,
        float_format="%.8e",
    )


def write_coastline(df: pd.DataFrame, path: str | PosixPath) -> None:
    """Write TESEO coastline and polygons files

    Args:
        df (pd.DataFrame): DataFrame with columns 'lon', 'lat' and polygons separated by nan lines (lon:[-180,180], lat:[-90,90])
        path (str | PosixPath): path to the new coastline-file
    """

    if "lon" not in df.keys().values or "lat" not in df.keys().values:
        raise ValueError("variable names in DataFrame should be 'lon' and 'lat'!")

    if df.shape[1] != 2:
        raise ValueError("DataFrame should contains column variables lon and lat only!")

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
    dir_path: str | PosixPath,
    filename_pattern: str = DEF_FILES["polygon_pattern"],
) -> None:
    """Write polygons from a coastline DataFrame

    Args:
        df (pd.DataFrame): input coastline DataFrame
        dir_path (str | PosixPath): directory where polygon files will be created
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


# 2. FORCINGS
def read_currents(path: str | PosixPath) -> Tuple[pd.DataFrame, float, float]:
    """Read TESEO currents-files (2dh: [lon, lat, u, v])

    Args:
        path (str | PosixPath): path to TESEO lstcurr.pre file

    Returns:
        Tuple[pd.DataFrame, float, float]: DataFrame of currents, number of files (times), and number of nodes
    """
    with open(path, "r") as f:
        files = [Path(path.parent, line.rstrip()) for line in f]

    df_list = _read_2dh_uv(files)

    n_rows = list(set([len(df.index) for df in df_list]))

    if len(n_rows) != 1:
        raise ValueError("Number of lines in each file are not equal!")

    return pd.concat(df_list), len(files), n_rows[0]


def read_winds(path: str | PosixPath) -> Tuple[pd.DataFrame, float, float]:
    """Read TESEO winds-files (2dh: [lon, lat, u, v])

    Args:
        path (str | PosixPath): path to TESEO lstwinds.pre file

    Returns:
        Tuple[pd.DataFrame, float, float]: DataFrame of winds, number of files (times), and number of nodes
    """
    with open(path, "r") as f:
        files = [Path(path.parent, line.rstrip()) for line in f]

    df_list = _read_2dh_uv(files)

    n_rows = list(set([len(df.index) for df in df_list]))

    if len(n_rows) != 1:
        raise ValueError("Number of lines in each file are not equal!")

    return pd.concat(df_list), len(files), n_rows[0]


def write_currents(df: pd.DataFrame, dir_path: PosixPath | str) -> None:
    """Write TESEO currents-files from a DataFrame

    Args:
        df (pd.DataFrame): DataFrame containing columns "time", "lon", "lat", "u", and "v".
        dir_path (PosixPath | str): directory path where will be created the files "lstcurr_UVW.pre" and all the "currents_*.txt"
    """

    lst_filename = DEF_FILES["currents_list"]
    file_pattern = DEF_FILES["currents_pattern"]
    path = Path(dir_path, lst_filename)

    _write_2dh_uv(df, path, file_pattern)


def write_winds(df: pd.DataFrame, dir_path: PosixPath | str) -> None:
    """Write TESEO winds-files from a DataFrame

    Args:
        df (pd.DataFrame): DataFrame containing columns "time", "lon", "lat", "u", and "v".
        dir_path (PosixPath | str): directory path where will be created the files "lstwinds.pre" and all the "winds_*.txt"
    """
    lst_filename = DEF_FILES["winds_list"]
    file_pattern = DEF_FILES["winds_pattern"]
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

    path = Path(path) if isinstance(path, str) else path

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


# def read_currents_depth_avg(path_list):
#     print("doing something...")


# def write_currents_depth_avg(dir_path):
#     print("doing something...")


# def read_waves(path_list):
#     print("doing something...")


# def write_waves(dir_path):
#     print("doing something...")


# # 3. CONFIGURATION
# def write_cfg(dir_path):
#     print("doing something...")


# def read_cfg(path):
#     print("doing something...")


# def write_run(dir_path):
#     print("doing something...")


# def read_run(path):
#     print("doing something...")


# # 4. RESULTS
def read_particles_results(
    dir_path: PosixPath | str,
    file_pattern: str = DEF_FILES["teseo_particles_pattern"],
) -> pd.DataFrame:
    """Load TESEO's particles results files "*_properties_*.txt" to DataFrame

    Args:
        dir_path (PosixPath | str): path to the results directory
        file_pattern (str, optional): file pattern of particles restuls. Defaults to "*_particles_*.txt".

    Returns:
        pd.DataFrame: Dataframe with all the results (including times and spill_id)
    """
    dir_path = Path(dir_path) if isinstance(dir_path, str) else dir_path

    files = list(dir_path.glob(file_pattern))
    if not files:
        raise ValueError(f"No files matching the pattern {file_pattern}")
    files.sort()

    dfs = [
        pd.read_csv(
            file,
            sep=",",
            header=0,
            encoding="iso-8859-1",
            skipinitialspace=True,
        )
        for file in files
    ]

    df = pd.concat(dfs).reset_index(drop=True)
    return _rename_results_names(df)


def read_properties_results(
    dir_path: PosixPath | str,
    file_pattern: str = DEF_FILES["teseo_properties_pattern"],
) -> pd.DataFrame:
    """Load TESEO's propierties results files "*_properties_*.txt" to DataFrame

    Args:
        dir_path (PosixPath | str): path to the results directory
        file_pattern (str, optional): file pattern of particles restuls. Defaults to "*_properties_*.txt".

    Returns:
        pd.DataFrame: Dataframe with all the results (including times and spill_id)
    """
    dir_path = Path(dir_path) if isinstance(dir_path, str) else dir_path

    files = list(dir_path.glob(file_pattern))
    if not files:
        raise ValueError(f"No files matching the pattern {file_pattern}")
    files.sort()

    spill_ids = [file.stem.split("_")[2] for file in files]

    dfs = []
    for file, spill_id in zip(files, spill_ids):
        df_ = pd.read_csv(
            file,
            sep=",",
            header=0,
            encoding="iso-8859-1",
            skipinitialspace=True,
        )
        df_["spill_id (-)"] = int(spill_id)

        dfs.append(df_)

    df = pd.concat(dfs).reset_index(drop=True)
    return _rename_results_names(df)


def read_grids_results(
    dir_path: PosixPath | str,
    file_pattern: str = DEF_FILES["teseo_grids_pattern"],
    fullgrid_filename: str = DEF_FILES["teseo_grid_coordinates"],
) -> pd.DataFrame:

    """Load TESEO's grids results files "*_grid_*.txt" to DataFrame

    Args:
        dir_path (PosixPath | str):  path to the results directory
        file_pattern (str, optional): file pattern of particles restuls. Defaults to DEF_FILES["teseo_grids_pattern"].
        fullgrid_filename (str, optional): filename of results coordinates domain-grid. Defaults to  DEF_FILES["teseo_grid_coordinates"].

    Returns:
        pd.DataFrame: Dataframe with all the results (including times and spill_id)
    """
    dir_path = Path(dir_path) if isinstance(dir_path, str) else dir_path
    files = list(dir_path.glob(file_pattern))
    if not files:
        raise ValueError(f"No files matching the pattern {file_pattern}")
    files.sort()

    spill_ids = [int(file.stem.split("_")[2]) for file in files]

    dfs = []
    for file, spill_id in zip(files, spill_ids):
        df_ = pd.read_csv(
            file,
            sep=",",
            header=0,
            encoding="iso-8859-1",
            skipinitialspace=True,
        )
        df_["spill_id (-)"] = spill_id

        dfs.append(df_)
    df = pd.concat(dfs)

    fullgrid = pd.read_csv(
        dir_path / fullgrid_filename,
        sep=",",
        header=0,
        encoding="iso-8859-1",
        skipinitialspace=True,
    )

    dfs = []
    for spill_id, df_spill in df.groupby("spill_id (-)"):
        minimum_grid = get_minimum_grid(fullgrid, df_spill)
        dfs.append(_add_inactive_cells(df_spill, minimum_grid, spill_id))
    df = pd.concat(dfs).reset_index(drop=True)
    return _rename_results_names(df)


def _rename_results_names(
    df: pd.DataFrame, coordname_map: dict = DEF_TESEO_RESULTS_MAP
) -> pd.DataFrame:
    """Rename variables according with map in default_names.json

    Args:
        df (pd.DataFrame): TESEO's results dataframe.
        coordname_map (dict, optional): map of variable names. Defaults to DEF_NAMES["teseo_results_map"].

    Returns:
        pd.DataFrame: renamed DataFrame
    """
    for key, value in coordname_map.items():
        df = df.rename(columns={key: value}) if key in df.keys() else df
    return df


def _add_inactive_cells(
    df_spill: pd.DataFrame, minimum_grid: pd.DataFrame, spill_id: int
) -> pd.DataFrame:
    """Concatenate active and inactive cells of grids results.

    Args:
        df_spill (pd.DataFrame): active celss for specific spill.
        minimum_grid (pd.DataFrame): minimum grid to represent the evolution of this specific spill.
        spill_id (int): spill identification number.

    Returns:
        pd.DataFrame: spill grid results in minimum grid-results area
    """
    full_df = []
    for time, df in df_spill.groupby("time (h)"):
        tmp = pd.concat([minimum_grid, df])
        tmp["spill_id (-)"] = spill_id
        tmp["time (h)"] = time
        full_df.append(tmp)

    return pd.concat(full_df).drop_duplicates(
        ["longitude (º)", "latitude (º)"], ignore_index=True, keep="last"
    )


def get_minimum_grid(fullgrid: pd.DataFrame, df_spill: pd.DataFrame) -> pd.DataFrame:
    """Obatain minimum grid area to represent the complete evolution for an specific spill.

    Args:
        fullgrid (pd.DataFrame): Full grid of results (usually equals to model domain).
        df_spill (pd.DataFrame): Results on active cells for specific spill.

    Returns:
        pd.DataFrame: minimum grid coordinates for represent this specific spill.
    """
    lon = (df_spill["longitude (º)"].min(), df_spill["longitude (º)"].max())
    lat = (df_spill["latitude (º)"].min(), df_spill["latitude (º)"].max())

    minimum_grid = fullgrid.loc[
        (fullgrid["longitude (º)"] >= lon[0])
        & (fullgrid["longitude (º)"] <= lon[1])
        & (fullgrid["latitude (º)"] >= lat[0])
        & (fullgrid["latitude (º)"] <= lat[1]),
        :,
    ]
    minimum_grid = minimum_grid.reset_index(drop=True)
    return minimum_grid


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
