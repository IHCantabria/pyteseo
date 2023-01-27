# """ Logic needed to define variables needed to write cfg and run files
# """

# # TODO - THINK, DEFINE MODULE AND ADD TASKS TO THE BACKLOG!!!


# def floater_release():
#     pass

from datetime import datetime
from pathlib import Path, PosixPath, WindowsPath
from shutil import copy

# grids --> 2 formats: "*.xyz" or "*.grid"
import pandas as pd

from pyteseo.defaults import DEF_FILES
from pyteseo.io.forcings import write_cte_currents, write_cte_waves, write_cte_winds


spill_points = [{}, {}]

substances = [{}, {}]  # List of required substances objects


def set_teseo_paths(
    domain_grid_path: str | PosixPath | WindowsPath = None,
    results_grid_path: str | PosixPath | WindowsPath = None,
    coastline_path: str | PosixPath | WindowsPath = None,
    lst_currents: str | PosixPath | WindowsPath = None,
    lst_winds: str | PosixPath | WindowsPath = None,
    lst_waves: str | PosixPath | WindowsPath = None,
    lst_currents_depthavg: str | PosixPath | WindowsPath = None,
    output_dir_path: str | PosixPath | WindowsPath = None,
) -> dict[Path]:

    if not domain_grid_path:
        raise ValueError("Domain grid is mandatory!")

    if not lst_waves and not lst_winds and not lst_waves:
        print("WARNING! You don't specify any forcing.")

    if not results_grid_path:
        results_grid_path = domain_grid_path

    if output_dir_path:
        copy(domain_grid_path, Path(output_dir_path, domain_grid_path.name))
        domain_grid_path = Path(output_dir_path, domain_grid_path.name)
        copy(results_grid_path, Path(output_dir_path, results_grid_path.name))
        results_grid_path = Path(output_dir_path, results_grid_path.name)
        if coastline_path:
            copy(coastline_path, Path(output_dir_path, coastline_path.name))
            coastline_path = Path(output_dir_path, coastline_path.name)

    else:
        output_dir_path = domain_grid_path.parent

    if not lst_currents:
        zero_df = pd.DataFrame({"time": [0], "u": [0], "v": [0]})
        write_cte_currents(df=zero_df, dir_path=output_dir_path)
        lst_currents = Path(output_dir_path, DEF_FILES["currents_list"])

    if not lst_winds:
        zero_df = pd.DataFrame({"time": [0], "u": [0], "v": [0]})
        write_cte_winds(df=zero_df, dir_path=output_dir_path)
        lst_winds = Path(output_dir_path, DEF_FILES["currents_list"])

    if not lst_waves:
        zero_df = pd.DataFrame({"time": [0], "hs": [0], "tp": [0], "dir": [0]})
        write_cte_waves(df=zero_df, dir_path=output_dir_path)
        lst_waves = Path(output_dir_path, DEF_FILES["waves_list"])

    return {
        "domain_grid_path": Path(domain_grid_path)
        if isinstance(domain_grid_path, str)
        else domain_grid_path,
        "results_grid_path": Path(results_grid_path)
        if isinstance(results_grid_path, str)
        else results_grid_path,
        "coastline_path": Path(coastline_path)
        if isinstance(coastline_path, str)
        else coastline_path,
        "lst_currents": Path(lst_currents)
        if isinstance(lst_currents, str)
        else lst_currents,
        "lst_winds": Path(lst_winds) if isinstance(lst_winds, str) else lst_winds,
        "lst_waves": Path(lst_waves) if isinstance(lst_waves, str) else lst_waves,
    }


def set_time(initial_datetime: datetime, duration_h: float, dt_s: float):
    return {
        "initial_datetime": initial_datetime,
        "durantion": duration_h,
        "time_step": dt_s,
    }


def set_climate_vars(
    air_temp: float, sea_temp: float, sea_dens: float, sea_c_visc: float
):

    return {
        "air_temperature": air_temp,
        "seawater_temperature": sea_temp,
        "seawater_density": sea_dens,
        "seawater_cinematic_viscosity": sea_c_visc,
    }


# instantaneous
def set_instantaneous_release_config(n_spill_points: int):
    return {"type": "instantaneous", "parameters": {"n_points": n_spill_points}}


# continuous
def set_continuous_release_config(
    n_spill_points: int, release_duration_h: float, dt_s_subspill: float
):

    return {
        "type": "continuous",
        "parameters": {
            "n_points": n_spill_points,
            "release_duration": release_duration_h,
            "dt_subspill": dt_s_subspill,
        },
    }


def set_parameters(
    dim: str, sim_type: str, realese_type: dict, backwards_flag: bool = False
):
    return {
        "dimensional_space": dim,  # 2D, quasi-3D, 3D
        "simulation_type": sim_type,  # drifter, oil, hns
        "motion_backwards": backwards_flag,
        "realese_type": realese_type,
    }


def set_spreading_config(type, duration_h):
    return {
        "type": type,
        "spreading_duration": duration_h,
    }


def set_processes(
    spreading_flag: bool,
    spreading_config: dict,
    evaporation_flag: bool,
    emulsification_flag: bool,
    vertical_dispersion_flag: bool,
    disolution_flag: bool,
    volatilization_flag: bool,
    sedimentation_flag: bool,
    biodegradation_flag: bool,
):
    return (
        {
            "spreading": spreading_flag,
            "spreading_config": spreading_config,
            "evaporation": evaporation_flag,
            "emulsification": emulsification_flag,
            "vertical_dispersion": vertical_dispersion_flag,
            "disolution": disolution_flag,
            "volatilization": volatilization_flag,
            "sedimentation": sedimentation_flag,
            "biodegradation": biodegradation_flag,
        },
    )
