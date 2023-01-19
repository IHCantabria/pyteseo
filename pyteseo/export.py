from __future__ import annotations

from pathlib import Path, PosixPath, WindowsPath
from geojson import Feature, FeatureCollection, MultiPoint, dump
from datetime import datetime, timedelta
import pandas as pd

from pyteseo.defaults import DEF_COORDS, DEF_FILES


# TODO - extend addition of utc_datetime to all the exportations


def export_particles(
    df: pd.DataFrame,
    file_format: str,
    output_dir: str | PosixPath | WindowsPath = "./",
    ref_datetime: datetime = None,
) -> list[PosixPath]:
    """Export TESEO's particles (by spill_id) to CSV, JSON, or GEOJSON.

    Args:
        df (pd.DataFrame): Particles data obtained with pyteseo.io.read_particles_results.
        file_format (str): csv, json, or geojson.
        output_dir (str | PosixPath | WindowsPath, optional): directory to export the files. Defaults to "./"
        ref_datetime (datetime): Reference datetime of the results. Defaults to None.

    Returns:
        list[PosixPath]: paths to exported files.
    """

    allowed_formats = ["csv", "json", "geojson"]
    exported_files = []

    output_dir = Path(output_dir)
    file_format = file_format.lower()
    if file_format not in allowed_formats:
        raise ValueError(
            f"Invalid format: {file_format}. Allowed formats {allowed_formats}"
        )
    else:
        output_path_pattern = Path(
            output_dir,
            DEF_FILES["export_particles_pattern"].replace(".*", f".{file_format}"),
        )

    for spill_id, df in df.groupby("spill_id"):
        output_path = Path(str(output_path_pattern).replace("*", f"{spill_id:03d}"))
        if file_format == "csv":
            df.to_csv(output_path, index=False)
        elif file_format == "json":
            df.to_json(output_path, orient="index")
        elif file_format == "geojson":
            if not ref_datetime:
                print("WARNING - You do not specify ")
                ref_datetime = datetime.utcnow()
            _df_particles_to_geojson(df, output_path, ref_datetime)
        exported_files.append(output_path)
        # NOTE - change for logging?
        print(
            f"\033[1;32m[spill_{spill_id:03d}] Particles successfully exported to {file_format.upper()} @ {output_path}\033[0;0m\n"
        )

    return exported_files


def _df_particles_to_geojson(
    df: pd.DataFrame,
    output_path: str | PosixPath | WindowsPath,
    ref_datetime: datetime,
) -> None:
    """Convert particles DataFrame to geojson using geojson library.

    Args:
        df (pd.DataFrame): Particles data readed with pyteseo.io.read_particles_results
        output_path (str | PosixPath | WindowsPath): path to create the exported file.
        ref_datetime (datetime, optional): Reference time of the results.
    """

    # Delete units from headers
    features = []
    df["ref_datetime"] = ref_datetime
    df["utc_datetime"] = df["ref_datetime"] + (df["time"] / 24).apply(timedelta)

    new_feature = Feature(
        geometry=MultiPoint(df[["lon", "lat"]].values.tolist()),
        properties={
            "times": df["utc_datetime"]
            .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            .values.tolist(),
            "status": df["status_index"].values.tolist(),
            "spill_id": df["spill_id"].values.tolist(),
        },
    )
    features.append(new_feature)

    with open(output_path, "w") as f:
        dump(FeatureCollection(features), f)


def export_properties(
    df: pd.DataFrame,
    file_format: list[str],
    output_dir: str | PosixPath | WindowsPath = "./",
) -> list[PosixPath]:
    """Export TESEO's properties (by spill_id) to CSV, or JSON.

    Args:
        df (pd.DataFrame): Properties data obtained with pyteseo.io.read_properties_results.
        file_format (list[str]): csv, or json.
        output_dir (str | PosixPath | WindowsPath, optional): directory to export the files. Defaults to "./"

    Returns:
        list[PosixPath]: paths to exported files.
    """

    allowed_formats = ["csv", "json"]
    exported_files = []

    output_dir = Path(output_dir)
    file_format = file_format.lower()
    if file_format not in allowed_formats:
        raise ValueError(f"Invalid format. Allowed formats {allowed_formats}")
    filename_pattern = DEF_FILES["export_properties_pattern"].replace(
        ".*", f".{file_format}"
    )
    path_pattern = output_dir / filename_pattern

    for spill_id, df in df.groupby("spill_id"):
        output_path = Path(str(path_pattern).replace("*", f"{spill_id:03d}"))
        if file_format == "csv":
            df.to_csv(output_path, index=False)
        elif file_format == "json":
            df.to_json(output_path, orient="index")
        exported_files.append(output_path)
        # NOTE - change for logging?
        print(
            f"\033[1;32m[spill_{spill_id:03d}] Properties successfully exported to {file_format.upper()} @ {output_path}\033[0;0m\n"
        )

    return exported_files


def export_grids(
    df: pd.DataFrame,
    file_format: list[str],
    output_dir: str | PosixPath | WindowsPath = "./",
) -> list[PosixPath]:
    """Export TESEO's grids (by spill_id) to CSV, JSON, or NETCDF.

    Args:
        df (pd.DataFrame): Grids data obtained with pyteseo.io.read_grids_results.
        file_format (list[str]): csv, json, or nc.
        output_dir (str | PosixPath | WindowsPath, optional): directory to export the files. Defaults to "./"

    Returns:
        list[PosixPath]: paths to exported files.
    """

    allowed_formats = ["csv", "json", "nc"]
    exported_files = []

    output_dir = Path(output_dir)
    file_format = file_format.lower()
    if file_format not in allowed_formats:
        raise ValueError(
            f"Invalid format: {file_format}. Allowed formats {allowed_formats}"
        )
    else:
        output_path_pattern = Path(
            output_dir,
            DEF_FILES["export_grids_pattern"].replace(".*", f".{file_format}"),
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
                    DEF_COORDS["t"],
                    DEF_COORDS["x"],
                    DEF_COORDS["y"],
                ]
            )
            ds = df.to_xarray().drop("spill_id")
            ds = _format_grid_netcdf(ds)
            ds.to_netcdf(output_path)
        exported_files.append(output_path)
        # NOTE - change for logging?
        print(
            f"\033[1;32m[spill_{spill_id:03d}] Grids successfully exported to {file_format.upper()} @ {output_path}\033[0;0m\n"
        )

    return exported_files


def _format_grid_netcdf(ds):
    return ds
