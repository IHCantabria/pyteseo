import numpy as np


def _check_cte_dt(df):
    dt = np.unique(np.diff(df["time"].unique()))
    if len(dt) > 1:
        print(f"WARNING: Forcing time steps are not constant {dt}")


def _check_lonlat_range(df):
    if (
        df.lon.max() >= 180
        or df.lon.min() <= -180
        or df.lat.max() >= 90
        or df.lat.min() <= -90
    ):
        print(
            "WARNING: lon and lat values should be inside ranges lon[-180,180] and lat[-90,90]!"
        )


def _check_lonlat_soting(df):
    if not df["lon"].is_monotonic_increasing:
        print("WARNING: lon values should be monotonic increasing!")
    if not df["lat"].is_monotonic_increasing:
        print("WARNING: lon values should be monotonic increasing!")


def _check_varnames(df, vars):
    for varname in vars:
        if varname not in df.keys():
            raise ValueError(f"{varname} not founded in the DataFrame")


def _check_n_vars(df, varnames):
    if df.shape[1] != len(varnames):
        raise ValueError(
            f"DataFrame has {df.shape[1]} columns not equal to vars: {varnames}!"
        )
