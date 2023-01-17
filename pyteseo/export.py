from __future__ import annotations

from pathlib import Path, PosixPath, WindowsPath

from pyteseo.io import (
    read_particles_results,
    read_properties_results,
    read_grids_results,
)


def particles_to_csv(
    dir_path: str | PosixPath | WindowsPath,
    output_path: str | PosixPath | WindowsPath = "particles.csv",
    file_pattern: str = "*_particles_*.txt",
) -> None:
    """Export TESEO's particles to CSV format

    Args:
        dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
        output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "particles.csv".
        file_pattern (str, optional): file pattern to search results. Defaults to "*_particles_*.txt".
    """

    output_path = Path(output_path) if isinstance(output_path, str) else output_path
    if output_path.suffix.lower() != ".csv":
        raise ValueError("output_path should have file extension '.csv'")

    df = read_particles_results(dir_path, file_pattern)
    df.to_csv(output_path, index=False)

    # NOTE - change for logging?
    print(f"Particles successfully exported to CSV @ {output_path}")


def particles_to_json(
    dir_path: str | PosixPath | WindowsPath,
    output_path: str | PosixPath | WindowsPath = "particles.csv",
    file_pattern: str = "*_particles_*.txt",
) -> None:
    """Export TESEO's particles to JSON format

    Args:
        dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
        output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "particles.csv".
        file_pattern (str, optional): file pattern to search results. Defaults to "*_particles_*.txt".
    """

    output_path = Path(output_path) if isinstance(output_path, str) else output_path
    if output_path.suffix.lower() != ".json":
        raise ValueError("output_path should have file extension '.json'")

    df = read_particles_results(dir_path, file_pattern)
    df.to_json(output_path, orient="index")

    # NOTE - change for logging?
    print(f"Particles successfully exported to JSON @ {output_path}")


# def particles_to_geojson():
#     # read_particles()
#     print("doing something...")


def properties_to_csv(
    dir_path: str | PosixPath | WindowsPath,
    output_path: str | PosixPath | WindowsPath = "properties.csv",
    file_pattern: str = "*_properties_*.txt",
) -> None:
    """Export TESEO's properties to CSV format

    Args:
        dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
        output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "properties.csv".
        file_pattern (str, optional): file pattern to search results. Defaults to "*_properties_*.txt".
    """

    output_path = Path(output_path) if isinstance(output_path, str) else output_path
    if output_path.suffix.lower() != ".csv":
        raise ValueError("output_path should have file extension '.csv'")

    df = read_properties_results(dir_path, file_pattern)
    df.to_csv(output_path, index=False)

    # NOTE - change for logging?
    print(f"Properties successfully exported to CSV @ {output_path}")


def properties_to_json(
    dir_path: str | PosixPath | WindowsPath,
    output_path: str | PosixPath | WindowsPath = "properties.csv",
    file_pattern: str = "*_properties_*.txt",
) -> None:
    """Export TESEO's properties to JSON format

    Args:
        dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
        output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "properties.csv".
        file_pattern (str, optional): file pattern to search results. Defaults to "*_properties_*.txt".
    """

    output_path = Path(output_path) if isinstance(output_path, str) else output_path
    if output_path.suffix.lower() != ".json":
        raise ValueError("output_path should have file extension '.json'")

    df = read_properties_results(dir_path, file_pattern)
    df.to_json(output_path, orient="index")

    # NOTE - change for logging?
    print(f"Properties successfully exported to JSON @ {output_path}")


def grids_to_csv(
    dir_path: str | PosixPath | WindowsPath,
    output_path: str | PosixPath | WindowsPath = "grids.csv",
    file_pattern: str = "*_grid_*.txt",
) -> None:
    """Export TESEO's grids to CSV format

    Args:
        dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
        output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "grids.csv".
        file_pattern (str, optional): file pattern to search results. Defaults to "*_grid_*.txt".
    """

    output_path = Path(output_path) if isinstance(output_path, str) else output_path
    if output_path.suffix.lower() != ".csv":
        raise ValueError("output_path should have file extension '.csv'")

    df = read_grids_results(dir_path, file_pattern)
    df.to_csv(output_path, index=False)

    # NOTE - change for logging?
    print(f"Grids successfully exported to CSV @ {output_path}")


def grids_to_json(
    dir_path: str | PosixPath | WindowsPath,
    output_path: str | PosixPath | WindowsPath = "grids.csv",
    file_pattern: str = "*_grid_*.txt",
) -> None:
    """Export TESEO's grids to JSON format

    Args:
        dir_path (str | PosixPath | WindowsPath): path to the TESEO's results directory
        output_path (str | PosixPath | WindowsPath, optional): csv ouput path. Defaults to "grids.csv".
        file_pattern (str, optional): file pattern to search results. Defaults to "*_grid_*.txt".
    """

    output_path = Path(output_path) if isinstance(output_path, str) else output_path
    if output_path.suffix.lower() != ".json":
        raise ValueError("output_path should have file extension '.json'")

    df = read_grids_results(dir_path, file_pattern)
    df.to_json(output_path, orient="index")

    # NOTE - change for logging?
    print(f"Grids successfully exported to JSON @ {output_path}")


# def grids_to_xarray():
#     # read_grids()
#     print("doing something...")


# def grids_to_netcdf():
#     # read_grids()
#     print("doing something...")
