import pytest
from pyteseo.io.substances import import_offline


@pytest.mark.parametrize(
    "substance_type, substance_name",
    [
        ("oil", "oil_example"),
        ("hns", "hns_example"),
    ],
)
def test_import_offline(substance_type, substance_name):
    substance = import_offline(substance_type, substance_name)

    assert bool(substance)
    assert isinstance(substance, dict)
    assert bool(substance)
