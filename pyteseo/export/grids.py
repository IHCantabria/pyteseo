from __future__ import annotations

from pathlib import Path
import pandas as pd

from pyteseo.defaults import DEF_COORDS, DEF_PATTERNS


# TODO - extend addition of utc_datetime to all the exportations


def export_grids(
    df: pd.DataFrame,
    file_format: list,
    output_dir: str = ".",
) -> list:
    """Export TESEO's grids (by spill_id) to CSV, JSON, or NETCDF

    Args:
        df (pd.DataFrame): Grids data obtained with pyteseo.io.read_grids_results
        file_format (list): csv, json, or nc
        output_dir (str, optional): directory to export the files. Defaults to "."

    Returns:
        list: paths to exported files
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
            DEF_PATTERNS["export_grids"].replace(".*", f".{file_format}"),
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
            ds = df.to_xarray().drop_vars("spill_id")
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
