from pathlib import Path
from shutil import rmtree
import pandas as pd
import pytest
from pyteseo.__init__ import __version__ as v
from pyteseo.export import (
    particles_to_csv,
    particles_to_json,
    properties_to_csv,
    properties_to_json,
    grids_to_csv,
    grids_to_json,
)
from pyteseo.io import (
    read_particles_results,
    read_properties_results,
    read_grids_results,
)


# TODO - Put a @fixture to setup the base path
data_path = Path(__file__).parent / "data"
tmp_path = Path(f"./tmp_pyteseo_{v}_tests")


@pytest.mark.parametrize(
    "dir_path, output_path, error",
    [
        (data_path, Path(tmp_path, "particles.csv"), None),
        ("not_existent_path", Path(tmp_path, "particles.csv"), "directory_not_exist"),
        (data_path, Path(tmp_path, "particles.json"), "file_extension"),
    ],
)
def test_particles_to_csv(dir_path, output_path, error):

    if not tmp_path.exists():
        tmp_path.mkdir()

    if error in ["directory_not_exist", "file_extension"]:
        with pytest.raises(ValueError):
            particles_to_csv(dir_path, output_path)
    else:
        particles_to_csv(dir_path, output_path)
        assert output_path.is_file()

    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "dir_path, output_path, error",
    [
        (data_path, Path(tmp_path, "particles.json"), None),
        ("not_existent_path", Path(tmp_path, "particles.json"), "directory_not_exist"),
        (data_path, Path(tmp_path, "particles.csv"), "file_extension"),
    ],
)
def test_particles_to_json(dir_path, output_path, error):

    if not tmp_path.exists():
        tmp_path.mkdir()

    if error in ["directory_not_exist", "file_extension"]:
        with pytest.raises(ValueError):
            particles_to_json(dir_path, output_path)
    else:
        particles_to_json(dir_path, output_path)
        assert output_path.is_file()
        df_json = pd.read_json(output_path, orient="index")
        df_teseo = read_particles_results(dir_path)
        assert df_json.shape == df_teseo.shape
        assert all(df_json.keys() == df_teseo.keys())

    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "dir_path, output_path, error",
    [
        (data_path, Path(tmp_path, "properties.csv"), None),
        ("not_existent_path", Path(tmp_path, "properties.csv"), "directory_not_exist"),
        (data_path, Path(tmp_path, "properties.json"), "file_extension"),
    ],
)
def test_properties_to_csv(dir_path, output_path, error):

    if not tmp_path.exists():
        tmp_path.mkdir()

    if error in ["directory_not_exist", "file_extension"]:
        with pytest.raises(ValueError):
            properties_to_csv(dir_path, output_path)
    else:
        properties_to_csv(dir_path, output_path)
        assert output_path.is_file()

    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "dir_path, output_path, error",
    [
        (data_path, Path(tmp_path, "properties.json"), None),
        ("not_existent_path", Path(tmp_path, "properties.json"), "directory_not_exist"),
        (data_path, Path(tmp_path, "properties.csv"), "file_extension"),
    ],
)
def test_properties_to_json(dir_path, output_path, error):

    if not tmp_path.exists():
        tmp_path.mkdir()

    if error in ["directory_not_exist", "file_extension"]:
        with pytest.raises(ValueError):
            properties_to_json(dir_path, output_path)
    else:
        properties_to_json(dir_path, output_path)
        assert output_path.is_file()
        df_json = pd.read_json(output_path, orient="index")
        df_teseo = read_properties_results(dir_path)
        assert df_json.shape == df_teseo.shape
        assert all(df_json.keys() == df_teseo.keys())

    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "dir_path, output_path, error",
    [
        (data_path, Path(tmp_path, "grids.csv"), None),
        ("not_existent_path", Path(tmp_path, "grids.csv"), "directory_not_exist"),
        (data_path, Path(tmp_path, "grids.json"), "file_extension"),
    ],
)
def test_grids_to_csv(dir_path, output_path, error):

    if not tmp_path.exists():
        tmp_path.mkdir()

    if error in ["directory_not_exist", "file_extension"]:
        with pytest.raises(ValueError):
            grids_to_csv(dir_path, output_path)
    else:
        grids_to_csv(dir_path, output_path)
        assert output_path.is_file()

    if tmp_path.exists():
        rmtree(tmp_path)


@pytest.mark.parametrize(
    "dir_path, output_path, error",
    [
        (data_path, Path(tmp_path, "grids.json"), None),
        ("not_existent_path", Path(tmp_path, "grids.json"), "directory_not_exist"),
        (data_path, Path(tmp_path, "grids.csv"), "file_extension"),
    ],
)
def test_grids_to_json(dir_path, output_path, error):

    if not tmp_path.exists():
        tmp_path.mkdir()

    if error in ["directory_not_exist", "file_extension"]:
        with pytest.raises(ValueError):
            grids_to_json(dir_path, output_path)
    else:
        grids_to_json(dir_path, output_path)
        assert output_path.is_file()
        df_json = pd.read_json(output_path, orient="index")
        df_teseo = read_grids_results(dir_path)
        assert df_json.shape == df_teseo.shape
        assert all(df_json.keys() == df_teseo.keys())

    if tmp_path.exists():
        rmtree(tmp_path)
