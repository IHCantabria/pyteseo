from pathlib import Path

import numpy as np
import pandas as pd
from datetime import timedelta

from pyteseo.defaults import DEF_COORDS, DEF_DIRS, DEF_FILES, DEF_VARS, DEF_PATTERNS
from pyteseo.io.domain import read_coastline, read_grid
from pyteseo.io.forcings import read_2d_forcing, read_cte_forcing, write_null_forcing
from pyteseo.io.results import (
    read_grids_results,
    read_particles_results,
    read_properties_results,
)
from pyteseo.io.cfg import write_cfg


class TeseoWrapper:
    def __init__(self, path: str):
        """wrapper of configuration, execution and postprocess of a TESEO's simulation.

        Args:
            path (str): path to the simulation folder.
        """
        path = Path(path).resolve()
        if not path.exists():
            path.mkdir(parents=True)

        input_dir = Path(path, DEF_DIRS["inputs"])
        if not input_dir.exists():
            input_dir.mkdir(parents=True)

        self.path = str(path)
        self.input_dir = str(input_dir)

    def load_inputs(
        self,
        currents_dt_cte: float = 1,
        winds_dt_cte: float = 1,
        waves_dt_cte: float = 1,
    ):
        """load input files in simulation 'inputs' directory

        Args:
            currents_dt_cte (float, optional): dt for spatially cte currents (hours). Defaults to 1.
            winds_dt_cte (float, optional):  dt for spatially cte winds (hours). Defaults to 1.
            waves_dt_cte (float, optional):  dt for spatially cte waves (hours). Defaults to 1.

        Raises:
            FileNotFoundError: grid file not founded in 'inputs' directory!
        """
        input_dir = Path(self.input_dir).resolve()

        print("Loading grid...")
        if Path(input_dir, DEF_FILES["grid"]).exists():
            self.grid = Grid(Path(input_dir, DEF_FILES["grid"]))
        else:
            raise FileNotFoundError("Grid-file is mandatory!")

        print("Loading coastline...")
        if Path(input_dir, DEF_FILES["coastline"]).exists():
            self.coastline = Coastline(Path(input_dir, DEF_FILES["coastline"]))
        else:
            print("No coastline defined!")

        print("Loading currents...")
        if Path(input_dir, DEF_FILES["currents"]).exists():
            self.currents = Currents(
                Path(input_dir, DEF_FILES["currents"]), currents_dt_cte
            )
        else:
            print("No currents defined, creating null currents...")
            self.currents = None
            write_null_forcing(input_dir, forcing_type="currents")

        print("Loading winds...")
        if Path(input_dir, DEF_FILES["winds"]).exists():
            self.winds = Winds(Path(input_dir, DEF_FILES["winds"]), winds_dt_cte)
        else:
            print("No winds defined, creating null winds...")
            self.winds = None
            write_null_forcing(input_dir, forcing_type="winds")

        print("Loading waves...")
        if Path(input_dir, DEF_FILES["waves"]).exists():
            self.waves = Waves(Path(input_dir, DEF_FILES["waves"]), waves_dt_cte)
        else:
            print("No waves defined, creating null waves...")
            self.waves = None
            write_null_forcing(input_dir, forcing_type="waves")

    def setup(self, parameters: dict):
        self.parameters = parameters

        # PARAMETERS TO BE FULLFILED FROM DEFAULTS IF THERE ARE NOT DEFINED IN INPUT_DICT
        if "seawater_kinematic_viscosity" not in self.parameters.keys():
            self.parameters["seawater_kinematic_viscosity"] = 1.004e-6

        if "seawater_temperature" not in self.parameters.keys():
            self.parameters["seawater_temperature"] = 17

        if "seawater_density" not in self.parameters.keys():
            self.parameters["seawater_density"] = 1025

        if "air_temperature" not in self.parameters.keys():
            self.parameters["air_temperature"] = 15.5

        if "suspended_solid_concentration" not in self.parameters.keys():
            self.parameters["suspended_solid_concentration"] = 10

        if "water_slope" not in self.parameters.keys():
            self.parameters["water_slope"] = 0.0005

        # PARAMETERS TO BE FULLFILED FROM CURRENT JOB ARGUMENTS
        if "inputs_directory" not in self.parameters.keys():
            self.parameters["inputs_directory"] = DEF_DIRS["inputs"] + "/"
        if "grid_filename" not in self.parameters.keys():
            self.parameters["grid_filename"] = Path(self.grid.path).name
        forcing_parameters = self._set_forcing_parameters()
        self.parameters["n_spill_points"] = len(self.parameters["spill_points"])

        if "continuous_release" in self.parameters.keys():
            self.parameters["release_type"] = "continuous"
            if "release_duration" or "release_timestep" not in self.parameters.keys():
                raise ValueError("release_duration or release_timestep not founded")
            if (
                self.parameters["release_duration"]
                or self.parameters["release_timestep"] == 0
            ):
                raise ValueError("release_duration and release_timestep can't be 0")
        else:
            self.parameters["release_type"] = "instantaneous"
            self.parameters["release_duration"] = timedelta(hours=0)
            self.parameters["release_timestep"] = timedelta(minutes=0)

        # DEFAULTS BY SUBSTANCE TYPE
        if self.parameters["substance_type"].lower() == "drifter":
            self.parameters["processes"] = {}
            self.parameters["processes"]["spreading"] = False
            self.parameters["processes"]["evaporation"] = False
            self.parameters["processes"]["emulsification"] = False
            self.parameters["processes"]["vertical_dispersion"] = False
            self.parameters["processes"]["dissolution"] = False
            self.parameters["processes"]["volatilization"] = False
            self.parameters["processes"]["sedimentation"] = False
            self.parameters["processes"]["biodegradation"] = False

        if self.parameters["substance_type"].lower() == "oil":
            if "processes" not in self.parameters.keys():
                self.parameters["processes"] = {}
                self.parameters["processes"]["spreading"] = False
                self.parameters["processes"]["evaporation"] = True
                self.parameters["processes"]["emulsification"] = True
                self.parameters["processes"]["vertical_dispersion"] = False
                self.parameters["processes"]["dissolution"] = False
                self.parameters["processes"]["volatilization"] = False
                self.parameters["processes"]["sedimentation"] = False
                self.parameters["processes"]["biodegradation"] = False

        if self.parameters["substance_type"].lower() == "hns":
            if "processes" not in self.parameters.keys():
                self.parameters["processes"] = {}
                self.parameters["processes"]["spreading"] = True
                self.parameters["processes"]["evaporation"] = True
                self.parameters["processes"]["emulsification"] = False
                self.parameters["processes"]["vertical_dispersion"] = False
                self.parameters["processes"]["dissolution"] = True
                self.parameters["processes"]["volatilization"] = True
                self.parameters["processes"]["sedimentation"] = False
                self.parameters["processes"]["biodegradation"] = False

                self.parameters["spreading"] = {}
                self.parameters["spreading"]["formulation"] = "mohid-hns"
                self.parameters["spreading"]["duration"] = timedelta(hours=0)

        if "spreading" not in self.parameters.keys():
            self.parameters["spreading"] = {}
        if "formulation" not in self.parameters["spreading"].keys():
            self.parameters["spreading"]["formulation"] = "adios2"
        if "duration" not in self.parameters["spreading"].keys():
            self.parameters["spreading"]["duration"] = timedelta(hours=0)

        self.cfg_parameters = parameters
        self.cfg_path = str(Path(self.path, DEF_PATTERNS["cfg"].replace("*", "teseo")))
        write_cfg(
            path=self.cfg_path,
            forcing_parameters=forcing_parameters,
            parameters=parameters,
        )

    def _set_forcing_parameters(self) -> dict:

        parameters = {}
        parameters["currents_nt"] = self.currents.nt
        parameters["winds_nt"] = self.winds.nt
        parameters["waves_nt"] = self.waves.nt
        parameters["currents_dt"] = self.currents.dt
        parameters["winds_dt"] = self.winds.dt
        parameters["waves_dt"] = self.waves.dt

        if self.currents.nx:
            parameters["currents_n_points"] = self.currents.nx * self.currents.ny
        else:
            parameters["currents_n_points"] = 1

        if self.winds.nx:
            parameters["winds_n_points"] = self.winds.nx * self.winds.ny
        else:
            parameters["winds_n_points"] = 1

        if self.waves.nx:
            parameters["waves_n_points"] = self.waves.nx * self.waves.ny
        else:
            parameters["waves_n_points"] = 1

        return parameters

    def run(self):
        self.run_path = Path(self.path, DEF_PATTERNS["run"].replace("*", "teseo"))
        pass

    @property
    def load_particles(self):
        read_particles_results(self.path)

    @property
    def load_properties(self):
        read_properties_results(self.path)

    @property
    def load_grids(self):
        read_grids_results(self.path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"


class Grid:
    def __init__(self, path: str):
        """centralize grid data and properties

        Args:
            path (str): path to grid file
        """
        self.path = str(Path(path).resolve())
        df = read_grid(self.path)
        self.calculate_variables(df)

    def calculate_variables(self, df):
        self.dx = _calculate_dx(df)
        self.dy = _calculate_dy(df)
        self.nx = _calculate_nx(df)
        self.ny = _calculate_ny(df)
        self.x_min = df[DEF_COORDS["x"]].min()
        self.x_max = df[DEF_COORDS["x"]].max()
        self.y_min = df[DEF_COORDS["y"]].min()
        self.y_max = df[DEF_COORDS["y"]].max()

    @property
    def load(self):
        return read_grid(self.path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"


class Coastline:
    def __init__(self, path: str):
        """centralize coastline data and properties

        Args:
            path (str): path to coastline file
        """
        self.path = str(Path(path).resolve())
        df = read_coastline(self.path)
        self.calculate_variables(df)

    def calculate_variables(self, df):
        self.x_min = df[DEF_COORDS["x"]].min()
        self.x_max = df[DEF_COORDS["x"]].max()
        self.y_min = df[DEF_COORDS["y"]].min()
        self.y_max = df[DEF_COORDS["y"]].max()
        self.n_polygons = len(df.index.get_level_values("polygon").unique())

    @property
    def load(self):
        return read_coastline(self.path)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"


class Currents:
    def __init__(self, lst_path: str, dt_cte: float = 1.0):
        """centralize currents data and properties

        Args:
            lst_path (str): path to lst-file of currents foncing
            dt_cte (float, optional): time step for currents if spatially cte. Defaults to 1.0.
        """
        self.forcing_type = "currents"
        self.varnames = DEF_VARS[self.forcing_type]
        self.path = str(Path(lst_path).resolve())

        if len(pd.read_csv(self.path, delimiter="\s+").columns) != 1:
            df = read_cte_forcing(self.path, self.forcing_type, dt_cte)
            self.dx = None
            self.dy = None
            self.dt = dt_cte
            self.nx = None
            self.ny = None
            self.nt = len(df)

        else:
            df = read_2d_forcing(self.path, self.forcing_type)

            self.dt = _calculate_dt(df)
            self.dx = _calculate_dx(df)
            self.dy = _calculate_dy(df)
            self.nt = _calculate_nt(df)
            self.nx = _calculate_nx(df)
            self.ny = _calculate_ny(df)

    @property
    def load(self):
        if self.dx:
            return read_2d_forcing(self.path, self.forcing_type)
        else:
            return read_cte_forcing(self.path, self.forcing_type, self.dt)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lst_path={self.path})"


class Winds:
    def __init__(self, lst_path: str, dt_cte: float = 1.0):
        """centralize winds data and properties

        Args:
            lst_path (str): path to lst-file of winds forcing
            dt_cte (float, optional): time step for winds if spatially cte. Defaults to 1.0.
        """
        self.forcing_type = "winds"
        self.varnames = DEF_VARS[self.forcing_type]
        self.path = str(Path(lst_path).resolve())

        if len(pd.read_csv(self.path, delimiter="\s+").columns) != 1:
            df = read_cte_forcing(self.path, self.forcing_type, dt_cte)
            self.dx = None
            self.dy = None
            self.dt = dt_cte
            self.nx = None
            self.ny = None
            self.nt = len(df)

        else:
            df = read_2d_forcing(self.path, self.forcing_type)

            self.dt = _calculate_dt(df)
            self.dx = _calculate_dx(df)
            self.dy = _calculate_dy(df)
            self.nt = _calculate_nt(df)
            self.nx = _calculate_nx(df)
            self.ny = _calculate_ny(df)

    @property
    def load(self):
        if self.dx:
            return read_2d_forcing(self.path, self.forcing_type)
        else:
            return read_cte_forcing(self.path, self.forcing_type, self.dt)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lst_path={self.path})"


class Waves:
    def __init__(self, lst_path: str, dt_cte: float = 1.0):
        """centralize wave data and properties

        Args:
            lst_path (str): path to lst-file of waves forcing.
            dt_cte (float, optional): time step for waves if spatially cte. Defaults to 1.0.
        """
        self.forcing_type = "waves"
        self.varnames = DEF_VARS[self.forcing_type]
        self.path = str(Path(lst_path).resolve())

        if len(pd.read_csv(self.path, delimiter="\s+").columns) != 1:
            df = read_cte_forcing(self.path, self.forcing_type, dt_cte)
            self.dx = None
            self.dy = None
            self.dt = dt_cte
            self.nx = None
            self.ny = None
            self.nt = len(df)
        else:
            df = read_2d_forcing(self.path, self.forcing_type)

            self.dt = _calculate_dt(df)
            self.dx = _calculate_dx(df)
            self.dy = _calculate_dy(df)
            self.nt = _calculate_nt(df)
            self.nx = _calculate_nx(df)
            self.ny = _calculate_ny(df)

    @property
    def load(self):
        if self.dx:
            return read_2d_forcing(self.path, self.forcing_type)
        else:
            return read_cte_forcing(self.path, self.forcing_type, self.dt)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(lst_path={self.path})"


def _calculate_dx(df: pd.DataFrame, coordname: str = DEF_COORDS["x"]):
    dx = np.unique(np.diff(df[coordname].unique()))
    if len(dx) == 1:
        return dx[0]
    else:
        print("WARNING: dx is not constant!")
        return dx[0]


def _calculate_dy(df: pd.DataFrame, coordname: str = DEF_COORDS["y"]):
    dy = np.unique(np.diff(df[coordname].unique()))
    if len(dy) == 1:
        return dy[0]
    else:
        print("WARNING: dy is not constant!")
        return dy[0]


def _calculate_dt(df: pd.DataFrame, coordname: str = DEF_COORDS["t"]):
    dt = np.unique(np.diff(df[coordname].unique()))
    if len(dt) == 1:
        return dt[0]
    else:
        print("WARNING: dt is not constant!")
        return dt[0]


def _calculate_nx(df: pd.DataFrame, coordname: str = DEF_COORDS["x"]):
    return len(df[coordname].unique())


def _calculate_ny(df: pd.DataFrame, coordname: str = DEF_COORDS["y"]):
    return len(df[coordname].unique())


def _calculate_nt(df: pd.DataFrame, coordname: str = DEF_COORDS["t"]):
    return len(df[coordname].unique())
