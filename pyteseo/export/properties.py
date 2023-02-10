from __future__ import annotations

from pathlib import Path
import pandas as pd

from pyteseo.defaults import FILE_PATTERNS


# TODO - extend addition of utc_datetime to all the exportations


def export_properties(
    df: pd.DataFrame,
    file_format: list,
    output_dir: str = ".",
) -> list:
    """Export TESEO's properties (by spill_id) to CSV, or JSON.

    Args:
        df (pd.DataFrame): Properties data obtained with pyteseo.io.read_properties_results.
        file_format (list): csv, or json.
        output_dir (str, optional): directory to export the files. Defaults to "."

    Returns:
        list: paths to exported files.
    """

    allowed_formats = ["csv", "json"]
    exported_files = []

    output_dir = Path(output_dir)
    file_format = file_format.lower()
    if file_format not in allowed_formats:
        raise ValueError(f"Invalid format. Allowed formats {allowed_formats}")
    filename_pattern = FILE_PATTERNS["export_properties"].replace(
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
