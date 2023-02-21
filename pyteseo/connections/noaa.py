import xarray as xr
import numpy as np
from datetime import datetime, timedelta


def access_forecast_global_winds(
    date: datetime, bbox: tuple[float, float, float, float]
):

    variables = ["ugrd10m", "vgrd10m"]
    ds = opendap_access_gfs_0p25_hourly(date)
    ds = ds.get(variables)
    ds = spatial_subset(ds, bbox)
    ds = ds.load()
    print("Load ok!")

    ds = reorder_0_360_to_m180_180(ds)
    ds = ds.resample(time="1H").interpolate("nearest")
    print("Resample ok!")
    ds = temporal_subset(ds, date)

    return ds


def reorder_0_360_to_m180_180(ds):
    attrs = ds.lon.attrs
    attrs["minimum"] = -180
    attrs["maximum"] = 180
    if ds.lon.values.max() > 180:
        ds = ds.assign_coords(lon=(ds.lon - 360))
    ds.lon.attrs = attrs
    print("Reorder longitudes to (-180, 180) ok!")
    return ds


def temporal_subset(ds: xr.Dataset, date_ini: datetime):
    return ds.sel(time=slice(date_ini, ds.time[-1].values))


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
    if bbox[0] < 0:
        bbox[0] = bbox[0] + 360
    if bbox[2] < 0:
        bbox[2] = bbox[2] + 360

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


def opendap_access_gfs_0p25_hourly(date):
    print(
        "\n Downloading from NOAA-NOMADS Opendap service. dataset: GFS 0.25º hourly \n"
    )
    if date > datetime.utcnow() + timedelta(days=5):
        raise ValueError("Not valid time.  Out of operational timerange")
    elif date < datetime.utcnow() - timedelta(days=10):
        raise ValueError("Not valid time. Out of operational timerange")

    if date > datetime.utcnow():
        date = datetime.utcnow()

    hour = int(date.hour / 6) * 6
    dataset_datetime = date.replace(hour=hour, minute=0, second=0, microsecond=0)
    dataset = f"gfs{dataset_datetime.strftime('%Y%m%d')}/gfs_0p25_1hr_{dataset_datetime.hour:02d}z"
    print(f"Dataset for requested {date.isoformat()} corresponds to {dataset=}")

    access = False
    while access is False:
        opendap_url = f"http://nomads.ncep.noaa.gov:80/dods/gfs_0p25_1hr/{dataset}"
        print(f"\nAccessing @ {dataset}")

        try:
            ds = xr.open_dataset(opendap_url)
            access = True
            print("\033[1;32m access successful! \U0001F642 \033[0;0m\n")
        except OSError as err:
            if err.errno == -72:
                raise err
            else:
                dataset_datetime -= timedelta(hours=6)
                dataset = f"gfs{dataset_datetime.strftime('%Y%m%d')}/gfs_0p25_1hr_{dataset_datetime.hour:02d}z"
            continue
        except RuntimeError as err:
            raise err

    return ds
