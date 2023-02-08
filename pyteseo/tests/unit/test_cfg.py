from datetime import datetime, timedelta
from pathlib import Path
from shutil import rmtree

import pandas as pd
import pytest

from pyteseo.__init__ import __version__ as v
from pyteseo.io.cfg import get_spill_points_df, get_substances_df

data_path = Path(__file__).parent.parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


def test_set_spill_point_df():
    df = get_spill_points_df(
        [
            {
                "release_time": datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                )
                + timedelta(minutes=80),
                "lon": -3.80,
                "lat": 43.44,
                "substance": "oil_example",
                "mass": 1000,
                "thickness": 0.15,
            },
            {
                "release_time": datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                )
                + timedelta(minutes=60),
                "lon": -3.879,
                "lat": 43.43,
                "substance": "oil_example",
                "mass": 1500,
                "thickness": 0.25,
            },
        ],
        datetime.utcnow().replace(minute=0, second=0, microsecond=0),
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert all(df["volume"].isnull())


def test_get_substance_df(
    substance_names=["oil_example", "oil_example"], substance_type="oil"
):
    substance_df = get_substances_df(substance_names, substance_type)
    assert len(substance_df) == len(substance_names)
    assert substance_df["density"].values[0] == 816
