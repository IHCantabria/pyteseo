from pyteseo.defaults import (
    DEF_COORDS,
    DEF_DIRS,
    DEF_FILES,
    DEF_VARS,
    DEF_TESEO_RESULTS_MAP,
)


def test_default_names():
    assert bool(DEF_DIRS) is True
    assert bool(DEF_FILES) is True
    assert bool(DEF_VARS) is True
    assert bool(DEF_TESEO_RESULTS_MAP) is True
    assert "x" in DEF_COORDS.keys()
    assert "y" in DEF_COORDS.keys()
    assert "z" in DEF_COORDS.keys()
    assert "t" in DEF_COORDS.keys()
