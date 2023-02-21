from datetime import datetime, timedelta

# import xarray as xr
from pyteseo.connections.noaa import access_forecast_global_winds


def test_gfs_0p25_hourly():

    lon_min = -5.5
    lon_max = -1
    lat_min = 43.25
    lat_max = 44.25

    bbox = [lon_min, lat_min, lon_max, lat_max]
    ds = access_forecast_global_winds(datetime.utcnow() - timedelta(hours=10), bbox)
    assert len(ds.time) <= 121


# def test_merge_overlaped_datasets():

#     paths = [
#         "gfs_20230214_00z.nc",
#         "gfs_20230214_06z.nc",
#         "gfs_20230214_12z.nc",
#         "gfs_20230214_18z.nc",
#     ]
#     paths.reverse()
#     ds = xr.Dataset()
#     for path in paths:
#         ds = ds.combine_first(xr.open_mfdataset(path))

#     assert ds.time.values[0] == xr.open_mfdataset(paths[3]).time.values[0]
#     assert ds.time.values[-1] == xr.open_mfdataset(paths[0]).time.values[-1]
#     assert (
#         ds.isel(time=13, lon=0, lat=0).gustsfc.values
#         == xr.open_mfdataset(paths[2]).isel(time=1, lon=0, lat=0).gustsfc.values
#     )
