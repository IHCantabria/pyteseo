from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import xarray as xr
from pydap.cas.get_cookies import setup_session
from pydap.client import open_url
from requests.sessions import Session


def access_global_currents(
    username: str,
    password: str,
    bbox: tuple[float, float, float, float],
    timebox: tuple[datetime, datetime],
) -> xr.Dataset:
    """access to CMEMS GLOBAL and get total currents (circulation + tide + stokes drift)

    Args:
        username (str): CMEMS username for login
        password (str): CMEMS password for login
        bbox (tuple[float, float, float, float]): lon_min, lat_min, lon_max, lat_max
        timebox (tuple[datetime, datetime]): initial_time, end_time

    Returns:
        xr.Dataset: resulting dataset with currents data (u, v)
    """
    opendap_url = (
        "https://nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy_anfc_merged-uv_PT1H-i"
    )
    varnames = ["utotal", "vtotal"]

    cmems = Cmems(username, password)
    ds = cmems.opendap_access(opendap_url)
    ds = ds.get(varnames)
    ds = ds.squeeze()
    ds = coords_standarization(ds, "time", "longitude", "latitude")
    ds = spatial_subset(ds, bbox)
    ds = temporal_subset(ds, timebox, buffer=timedelta(hours=1))
    ds = ds.rename(
        {varname: new_varname for varname, new_varname in zip(varnames, ["u", "v"])}
    )

    return ds


def access_global_winds(
    username: str,
    password: str,
    bbox: tuple[float, float, float, float],
    timebox: tuple[datetime, datetime],
) -> xr.Dataset:
    """access to CMEMS GLOBAL L4-SATELLITE winds

    Args:
        username (str): CMEMS username for login
        password (str): CMEMS password for login
        bbox (tuple[float, float, float, float]): lon_min, lat_min, lon_max, lat_max
        timebox (tuple[datetime, datetime]): initial_time, end_time

    Returns:
        xr.Dataset: resulting dataset with winds data (u, v)
    """
    opendap_url = "https://nrt.cmems-du.eu/thredds/dodsC/cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H"
    varnames = ["eastward_wind", "northward_wind"]

    cmems = Cmems(username, password)
    ds = cmems.opendap_access(opendap_url)
    ds = ds.get(varnames)
    ds = spatial_subset(ds, bbox)
    ds = temporal_subset(ds, timebox, buffer=timedelta(hours=1))
    ds = ds.rename(
        {varname: new_varname for varname, new_varname in zip(varnames, ["u", "v"])}
    )

    return ds


class Cmems:
    cas_url = "https://cmems-cas.cls.fr/cas/login"

    def __init__(self, username: str, password: str) -> Session:
        self.session = setup_session(self.cas_url, username, password)
        self.session.cookies.set("CASTGC", self.session.cookies.get_dict()["CASTGC"])
        print(f"\033[1;32m {username=} login successful! \U0001F642 \033[0;0m\n")

    def opendap_access(self, opendap_url) -> xr.Dataset:
        data_store = xr.backends.PydapDataStore(
            open_url(url=opendap_url, session=self.session)
        )
        return xr.open_dataset(data_store)


def coords_standarization(
    ds: xr.Dataset,
    ds_t: str,
    ds_x: str,
    ds_y: str,
    ds_z: str = None,
    standard_t: str = "time",
    standard_x: str = "lon",
    standard_y: str = "lat",
    standard_z: str = "depth",
) -> xr.Dataset:
    """standarize main coordinates (t,x,y,z)

    Args:
        ds (xr.Dataset): input dataset.
        ds_t (str): dataset's name for t-coordinate.
        ds_x (str): dataset's name for x-coordinate.
        ds_y (str): dataset's name for y-coordinate.
        ds_z (str, optional): dataset's name for z-coordinate. Defaults to None.
        standard_t (str, optional): standard name for t-coordinate. Defaults to "time".
        standard_x (str, optional): standard name for x-coordinate. Defaults to "lon".
        standard_y (str, optional): standard name for y-coordinate. Defaults to "lat".
        standard_z (str, optional): standard name for z-coordinate. Defaults to "depth".

    Returns:
        xr.Dataset: formatted dataset.
    """
    if ds_z:
        return ds.rename(
            {ds_t: standard_t, ds_x: standard_x, ds_y: standard_y, ds_z: standard_z}
        )
    else:
        return ds.rename({ds_t: standard_t, ds_x: standard_x, ds_y: standard_y})


def spatial_subset(
    ds: xr.Dataset, bbox: tuple[float, float, float, float], buffer: bool = True
) -> xr.Dataset:
    """subset spatially (lon,lat).

    Args:
        ds (xr.Dataset): input dataset.
        bbox (tuple[float, float, float, float]): lon_min, lat_min, lon_max, lat_max coordinates.
        buffer (bool, optional): extends selection to the next outside coordinate. Defaults to None.

    Returns:
        xr.Dataset: subset dataset
    """
    if buffer:
        dx = max(np.unique(ds["lon"].diff("lon").values))
        dy = max(np.unique(ds["lat"].diff("lat").values))

        buffer_value = max([dx, dy])
        return ds.sel(
            lon=slice(bbox[0] - buffer_value, bbox[2] + buffer_value),
            lat=slice(bbox[1] - buffer_value, bbox[3] + buffer_value),
        )
    else:
        return ds.sel(
            lon=slice(bbox[0], bbox[2]),
            lat=slice(bbox[1], bbox[3]),
        )


def temporal_subset(
    ds: xr.Dataset, timebox: tuple[datetime, datetime], buffer: timedelta = None
) -> xr.Dataset:
    """subset temporally.

    Args:
        ds (xr.Dataset): input dataset.
        time_box (tuple[datetime, datetime]): initial_datetime, end_datetime.
        buffer (timedelta): time to extend selection limits.

    Returns:
        xr.Dataset: subset dataset
    """
    if buffer:
        return ds.sel(time=slice(timebox[0] - buffer, timebox[1] + buffer))
    else:
        return ds.sel(time=slice(timebox[0], timebox[1]))


def subset_ds(
    ds: xr.Dataset,
    bbox: tuple,
    t_min: datetime,
    t_max: datetime,
    buffer_dx=0.1,
):
    ds = ds.sel(
        lon=slice(bbox[0] - buffer_dx, bbox[2] + buffer_dx),
        lat=slice(bbox[1] - buffer_dx, bbox[3] + buffer_dx),
    )

    new_ds = ds.sel(time=slice(t_min, t_max))
    if pd.to_datetime(ds.time[-1].values).to_pydatetime() < t_max:
        dt = float(np.unique(ds.time.diff("time").dt.seconds)[0])
        t_max = t_max + timedelta(seconds=dt)

    return new_ds
