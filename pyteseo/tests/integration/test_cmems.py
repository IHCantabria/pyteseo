import os
from datetime import datetime, timedelta

import pandas as pd
import xarray as xr
from requests.sessions import Session

from pyteseo.connections.cmems import (
    Cmems,
    coords_standarization,
    spatial_subset,
    temporal_subset,
    access_global_currents,
    access_global_winds,
)

username = os.environ.get("CMEMS_username")
password = os.environ.get("CMEMS_password")
opendap_url = (
    "https://nrt.cmems-du.eu/thredds/dodsC/cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H"
)
bbox = (-4.25, 43.2, -1.25, 44)
timebox = (datetime(2021, 3, 1, 0, 5, 0), datetime(2021, 3, 6, 0, 12, 0))


def test_login():
    cmems = Cmems(username, password)
    assert isinstance(cmems.session, Session)
    assert "CASTGC" in cmems.session.cookies.get_dict()


def test_access_opendap():

    cmems = Cmems(username, password)
    ds = cmems.opendap_access(opendap_url)

    assert isinstance(ds, xr.Dataset)
    assert "lon" in ds.coords
    assert "lat" in ds.coords
    assert "time" in ds.coords


def test_coords_standarization():

    cmems = Cmems(username, password)
    ds = cmems.opendap_access(opendap_url)
    ds2 = coords_standarization(ds, "time", "lon", "lat")
    assert "lon" in ds2.coords
    assert "lat" in ds2.coords
    assert "time" in ds2.coords


def test_spatial_subset():

    cmems = Cmems(username, password)
    ds = cmems.opendap_access(opendap_url)
    ds = coords_standarization(ds, "time", "lon", "lat")
    ds2 = spatial_subset(ds, bbox)
    assert ds.lon[0].values < ds2.lon[0].values
    assert ds.lon[-1].values > ds2.lon[-1].values
    assert ds.lat[0].values < ds2.lat[0].values
    assert ds.lat[-1].values > ds2.lon[-1].values


def test_temporal_subset():

    cmems = Cmems(username, password)
    ds = cmems.opendap_access(opendap_url)
    ds = coords_standarization(ds, "time", "lon", "lat")
    ds2 = temporal_subset(ds, timebox, buffer=timedelta(hours=1))
    assert ds.time[0].values < ds2.time[0].values
    assert ds.time[-1].values > ds2.time[-1].values


def test_access_global_currents():

    ds = access_global_currents(username, password, bbox, timebox)
    assert bbox[0] > ds.lon[0]
    assert bbox[2] < ds.lon[-1]
    assert bbox[1] > ds.lat[0]
    assert bbox[3] < ds.lat[-1]
    assert timebox[0] > pd.to_datetime(ds.time[0].values)
    assert timebox[1] < pd.to_datetime(ds.time[-1].values)
    assert "u" in ds.variables
    assert "v" in ds.variables


def test_access_global_winds():

    ds = access_global_winds(username, password, bbox, timebox)
    assert bbox[0] > ds.lon[0]
    assert bbox[2] < ds.lon[-1]
    assert bbox[1] > ds.lat[0]
    assert bbox[3] < ds.lat[-1]
    assert timebox[0] > pd.to_datetime(ds.time[0].values)
    assert timebox[1] < pd.to_datetime(ds.time[-1].values)
    assert "u" in ds.variables
    assert "v" in ds.variables
