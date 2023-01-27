from pathlib import Path
from shutil import rmtree

import pytest

from pyteseo.__init__ import __version__ as v


data_path = Path(__file__).parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")


@pytest.fixture
def setup_teardown():
    if not tmp_path.exists():
        tmp_path.mkdir()
    yield
    if tmp_path.exists():
        rmtree(tmp_path)


def test_write_cfg():
    pass
    # auto_parameters =

    # user_parameters

    # write_cfg(parameters, path)
    # assert path.exist()
