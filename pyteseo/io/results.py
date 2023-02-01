"""Input and Output functionality for specific TESEO file formats
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pyteseo.defaults import DEF_FILES, DEF_PATTERNS, DEF_TESEO_RESULTS_MAP


# # 4. RESULTS
def read_particles_results(
    dir_path: str,
    file_pattern: str = DEF_PATTERNS["teseo_particles"],
) -> pd.DataFrame:
    """Load TESEO's particles results files "*_properties_*.txt" to DataFrame

    Args:
        dir_path (str): path to the results directory
        file_pattern (str, optional): file pattern of particles restuls. Defaults to "*_particles_*.txt".

    Returns:
        pd.DataFrame: Dataframe with all the results (including times and spill_id)
    """
    dir_path = Path(dir_path)

    files = sorted(list(dir_path.glob(file_pattern)))
    if not files:
        raise FileNotFoundError(f"No files matching the pattern {file_pattern}")
    else:
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
    dir_path: str,
    file_pattern: str = DEF_PATTERNS["teseo_properties"],
) -> pd.DataFrame:
    """Load TESEO's propierties results files "*_properties_*.txt" to DataFrame

    Args:
        dir_path (str): path to the results directory
        file_pattern (str, optional): file pattern of particles restuls. Defaults to "*_properties_*.txt".

    Returns:
        pd.DataFrame: Dataframe with all the results (including times and spill_id)
    """
    dir_path = Path(dir_path)

    files = sorted(list(dir_path.glob(file_pattern)))
    if not files:
        raise FileNotFoundError(f"No files matching the pattern {file_pattern}")
    else:
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
    dir_path: str,
    file_pattern: str = DEF_PATTERNS["teseo_grids"],
    fullgrid_filename: str = DEF_FILES["teseo_grid_coordinates"],
) -> pd.DataFrame:

    """Load TESEO's grids results files "*_grid_*.txt" to DataFrame

    Args:
        dir_path (PosixPath | str):  path to the results directory
        file_pattern (str, optional): file pattern of particles restuls. Defaults to DEF_PATTERNS["teseo_grids"].
        fullgrid_filename (str, optional): filename of results coordinates domain-grid. Defaults to  DEF_FILES["teseo_grid_coordinates"].

    Returns:
        pd.DataFrame: Dataframe with all the results (including times and spill_id)
    """
    dir_path = Path(dir_path) if isinstance(dir_path, str) else dir_path
    files = sorted(list(dir_path.glob(file_pattern)))
    if not files:
        raise FileNotFoundError(f"No files matching the pattern {file_pattern}")
    else:
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
