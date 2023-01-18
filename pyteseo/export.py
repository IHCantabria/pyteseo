from __future__ import annotations

from pathlib import Path, PosixPath, WindowsPath
from pandas import DataFrame

from pyteseo.__init__ import DEF_NAMES


def export_particles(
    df: DataFrame,
    file_format: list[str],
    output_dir: str | PosixPath | WindowsPath = "./",
) -> list[PosixPath]:
    """Export TESEO's particles (by spill_id) to CSV, JSON, or GEOJSON.

    Args:
        df (DataFrame): Particles data obtained with pyteseo.io.read_particles_results.
        file_format (list[str]): csv, json, or geojson.
        output_dir (str | PosixPath | WindowsPath, optional): directory to export the files. Defaults to "./"

    Returns:
        list[PosixPath]: paths to exported files.
    """

    allowed_formats = ["csv", "json", "geojson"]
    exported_files = []

    output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir

    file_format = file_format.lower()
    if file_format not in allowed_formats:
        raise ValueError(
            f"Invalid format: {file_format}. Allowed formats {allowed_formats}"
        )
    else:
        output_path_pattern = Path(
            output_dir,
            DEF_NAMES["files"]["export_particles_pattern"].replace(
                ".*", f".{file_format}"
            ),
        )

    for spill_id, df in df.groupby("spill_id"):
        output_path = Path(str(output_path_pattern).replace("*", f"{spill_id:03d}"))
        if file_format == "csv":
            df.to_csv(output_path, index=False)
        elif file_format == "json":
            df.to_json(output_path, orient="index")
        elif file_format == "geojson":
            raise NotImplementedError("not implemented yet!")
            # TODO _df_to_geojson()
        exported_files.append(output_path)
        # NOTE - change for logging?
        print(
            f"Particles {spill_id} successfully exported to {file_format.upper()} @ {output_path}"
        )

    return exported_files


# def _particles_df_to_geojson():
#     print("doing something...")


def export_properties(
    df: DataFrame,
    file_format: list[str],
    output_dir: str | PosixPath | WindowsPath = "./",
) -> list[PosixPath]:
    """Export TESEO's properties (by spill_id) to CSV, or JSON.

    Args:
        df (DataFrame): Properties data obtained with pyteseo.io.read_properties_results.
        file_format (list[str]): csv, or json.
        output_dir (str | PosixPath | WindowsPath, optional): directory to export the files. Defaults to "./"

    Returns:
        list[PosixPath]: paths to exported files.
    """

    allowed_formats = ["csv", "json"]
    exported_files = []

    output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir

    file_format = file_format.lower()
    if file_format not in allowed_formats:
        raise ValueError(
            f"Invalid format: {file_format}. Allowed formats {allowed_formats}"
        )
    else:
        output_path_pattern = Path(
            output_dir,
            DEF_NAMES["files"]["export_properties_pattern"].replace(
                ".*", f".{file_format}"
            ),
        )

    for spill_id, df in df.groupby("spill_id"):
        output_path = Path(str(output_path_pattern).replace("*", f"{spill_id:03d}"))
        if file_format == "csv":
            df.to_csv(output_path, index=False)
        elif file_format == "json":
            df.to_json(output_path, orient="index")
        exported_files.append(output_path)
        # NOTE - change for logging?
        print(
            f"Properties {spill_id} successfully exported to {file_format.upper()} @ {output_path}"
        )

    return exported_files


def export_grids(
    df: DataFrame,
    file_format: list[str],
    output_dir: str | PosixPath | WindowsPath = "./",
) -> list[PosixPath]:
    """Export TESEO's grids (by spill_id) to CSV, JSON, or NETCDF.

    Args:
        df (DataFrame): Grids data obtained with pyteseo.io.read_grids_results.
        file_format (list[str]): csv, json, or nc.
        output_dir (str | PosixPath | WindowsPath, optional): directory to export the files. Defaults to "./"

    Returns:
        list[PosixPath]: paths to exported files.
    """

    allowed_formats = ["csv", "json", "nc"]
    exported_files = []

    output_dir = Path(output_dir) if isinstance(output_dir, str) else output_dir

    file_format = file_format.lower()
    if file_format not in allowed_formats:
        raise ValueError(
            f"Invalid format: {file_format}. Allowed formats {allowed_formats}"
        )
    else:
        output_path_pattern = Path(
            output_dir,
            DEF_NAMES["files"]["export_grids_pattern"].replace(".*", f".{file_format}"),
        )

    for spill_id, df in df.groupby("spill_id"):
        output_path = Path(str(output_path_pattern).replace("*", f"{spill_id:03d}"))
        if file_format == "csv":
            df.to_csv(output_path, index=False)
        elif file_format == "json":
            df.to_json(output_path, orient="index")
        elif file_format == "nc":
            df = df.set_index(
                [
                    DEF_NAMES["coords"]["t"],
                    DEF_NAMES["coords"]["x"],
                    DEF_NAMES["coords"]["y"],
                ]
            )
            ds = df.to_xarray().drop("spill_id")
            ds = _format_grid_netcdf(ds)
            ds.to_netcdf(output_path)
        exported_files.append(output_path)
        # NOTE - change for logging?
        print(
            f"Grids {spill_id} successfully exported to {file_format.upper()} @ {output_path}"
        )

    return exported_files


def _format_grid_netcdf(ds):
    return ds


# def properties_to_csv(
#     dir_path: str | PosixPath | WindowsPath,
#     output_path: str | PosixPath | WindowsPath = "properties.csv",
#     file_pattern: str = "*_properties_*.txt",
# ) -> None:
#     """Export TESEO's properties to CSV format

#     Args:
#         dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
#         output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "properties.csv".
#         file_pattern (str, optional): file pattern to search results. Defaults to "*_properties_*.txt".
#     """

#     output_path = Path(output_path) if isinstance(output_path, str) else output_path
#     if output_path.suffix.lower() != ".csv":
#         raise ValueError("output_path should have file extension '.csv'")

#     df = read_properties_results(dir_path, file_pattern)
#     df.to_csv(output_path, index=False)

#     # NOTE - change for logging?
#     print(f"Properties successfully exported to CSV @ {output_path}")


# def properties_to_json(
#     dir_path: str | PosixPath | WindowsPath,
#     output_path: str | PosixPath | WindowsPath = "properties.csv",
#     file_pattern: str = "*_properties_*.txt",
# ) -> None:
#     """Export TESEO's properties to JSON format

#     Args:
#         dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
#         output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "properties.csv".
#         file_pattern (str, optional): file pattern to search results. Defaults to "*_properties_*.txt".
#     """

#     output_path = Path(output_path) if isinstance(output_path, str) else output_path
#     if output_path.suffix.lower() != ".json":
#         raise ValueError("output_path should have file extension '.json'")

#     df = read_properties_results(dir_path, file_pattern)
#     df.to_json(output_path, orient="index")

#     # NOTE - change for logging?
#     print(f"Properties successfully exported to JSON @ {output_path}")


# def grids_to_csv(
#     dir_path: str | PosixPath | WindowsPath,
#     output_path: str | PosixPath | WindowsPath = "grids.csv",
#     file_pattern: str = "*_grid_*.txt",
# ) -> None:
#     """Export TESEO's grids to CSV format

#     Args:
#         dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
#         output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "grids.csv".
#         file_pattern (str, optional): file pattern to search results. Defaults to "*_grid_*.txt".
#     """

#     output_path = Path(output_path) if isinstance(output_path, str) else output_path
#     if output_path.suffix.lower() != ".csv":
#         raise ValueError("output_path should have file extension '.csv'")

#     df = read_grids_results(dir_path, file_pattern)
#     df.to_csv(output_path, index=False)

#     # NOTE - change for logging?
#     print(f"Grids successfully exported to CSV @ {output_path}")


# def grids_to_json(
#     dir_path: str | PosixPath | WindowsPath,
#     output_path: str | PosixPath | WindowsPath = "grids.csv",
#     file_pattern: str = "*_grid_*.txt",
# ) -> None:
#     """Export TESEO's grids to JSON format

#     Args:
#         dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
#         output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "grids.csv".
#         file_pattern (str, optional): file pattern to search results. Defaults to "*_grid_*.txt".
#     """

#     output_path = Path(output_path) if isinstance(output_path, str) else output_path
#     if output_path.suffix.lower() != ".json":
#         raise ValueError("output_path should have file extension '.json'")

#     df = read_grids_results(dir_path, file_pattern)
#     df.to_json(output_path, orient="index")

#     # NOTE - change for logging?
#     print(f"Grids successfully exported to JSON @ {output_path}")


# def grids_to_netcdf(
#     dir_path: str | PosixPath | WindowsPath,
#     output_dir_path: str | PosixPath | WindowsPath = "./",
#     output_file_pattern: str
#     | PosixPath
#     | WindowsPath = DEF_NAMES["files"]["export_grids_pattern"],
#     file_pattern: str = DEF_NAMES["files"]["teseo_grids_pattern"],
# ) -> list:
#     """Export TESEO's grids (*_grid_*.txt) to NetCDF format

#     Args:
#         dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
#         output_dir_path (str | PosixPath | WindowsPath): directory to export results
#         output_file_pattern (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to DEF_NAMES["files"]["export_grids_pattern"].
#         file_pattern (str, optional): file pattern to search results. Defaults to DEF_NAMES["files"]["teseo_grids_pattern"].
#     """
#     output_path_pattern = Path(output_dir_path, Path(output_file_pattern).stem + ".nc")

#     df = read_grids_results(dir_path, file_pattern)
#     # Rename columns
#     new_keys = ["lon", "lat", "time", "mass", "probability", "particles", "spill_id"]
#     map_columns = {key: value for key, value in zip(df.keys(), new_keys)}
#     df = df.rename(columns=map_columns)

#     df = df.set_index(["time", "lon", "lat"])
#     output_paths = []
#     for spill_id, df_tmp in df.groupby("spill_id"):
#         ds = df_tmp.to_xarray().drop("spill_id")
#         output_path = Path(
#             output_path_pattern.parent,
#             output_path_pattern.name.replace("*", f"{spill_id:03d}"),
#         )
#         ds.to_netcdf(output_path)
#         output_paths.append(output_path)
#         # NOTE - change for logging?
#         print(f"Grids {spill_id:03d} successfully exported to NetCDF @ {output_path}")

#     return output_paths
