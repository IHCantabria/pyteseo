from __future__ import annotations

from pathlib import Path
from geojson import Feature, FeatureCollection, MultiPoint, dump
from datetime import datetime, timedelta
import pandas as pd

from pyteseo.defaults import DEF_PATTERNS


# TODO - extend addition of utc_datetime to all the exportations


def export_particles(
    df: pd.DataFrame,
    file_format: str,
    output_dir: str = ".",
    ref_datetime: datetime = None,
) -> list:
    """Export TESEO's particles (by spill_id) to CSV, JSON, or GEOJSON.

    Args:
        df (pd.DataFrame): Particles data obtained with pyteseo.io.read_particles_results
        file_format (str): csv, json, or geojson
        output_dir (str, optional): directory to export the files. Defaults to "."
        ref_datetime (datetime): Reference datetime of the results. Defaults to None

    Returns:
        list: paths to exported files.
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
            DEF_PATTERNS["export_particles"].replace(".*", f".{file_format}"),
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
    output_path: str,
    ref_datetime: datetime,
) -> None:
    """Convert particles DataFrame to geojson using geojson library.

    Args:
        df (pd.DataFrame): Particles data readed with pyteseo.io.read_particles_results
        output_dir (str): directory to export the files
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
