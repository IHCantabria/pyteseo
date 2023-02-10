from pyteseo.defaults import (
    COORDINATE_NAMES,
    DIRECTORY_NAMES,
    FILE_NAMES,
    VARIABLE_NAMES,
    RESULTS_MAP,
)


def test_default_names():
    assert bool(DIRECTORY_NAMES) is True
    assert bool(FILE_NAMES) is True
    assert bool(VARIABLE_NAMES) is True
    assert bool(RESULTS_MAP) is True
    assert "x" in COORDINATE_NAMES.keys()
    assert "y" in COORDINATE_NAMES.keys()
    assert "z" in COORDINATE_NAMES.keys()
    assert "t" in COORDINATE_NAMES.keys()
