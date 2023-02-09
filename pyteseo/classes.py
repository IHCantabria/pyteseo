from pathlib import Path

import numpy as np
import pandas as pd

from pyteseo.defaults import DEF_COORDS, DEF_DIRS, DEF_FILES, DEF_PATTERNS, DEF_VARS
from pyteseo.io.cfg import (
    _complete_cfg_parameters,
    check_user_minimum_parameters,
    write_cfg,
)
from pyteseo.io.domain import read_coastline, read_grid
from pyteseo.io.forcings import read_2d_forcing, read_cte_forcing, write_null_forcing
from pyteseo.io.results import (
    read_grids_results,
    read_particles_results,
    read_properties_results,
)


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

    def setup(self, user_parameters: dict):

        check_user_minimum_parameters(user_parameters)

        self.setup_cfg(user_parameters)

        # TODO
        # self.setup_run(user_parameters)

    def setup_cfg(self, user_parameters):

        self.cfg_path = str(Path(self.path, DEF_PATTERNS["cfg"].replace("*", "teseo")))

        self.parameters = _complete_cfg_parameters(user_parameters)
        forcing_parameters = self._forcing_parameters
        file_parameters = self._file_parameters

        write_cfg(
            path=self.cfg_path,
            file_parameters=file_parameters,
            forcing_parameters=forcing_parameters,
            simulation_parameters=self.parameters,
        )

    @property
    def _file_parameters(self) -> dict:
        d = {}
        d["inputs_directory"] = DEF_DIRS["inputs"] + "/"
        d["grid_filename"] = Path(self.grid.path).name
        return d

    @property
    def _forcing_parameters(self) -> dict:
        d = {}
        d["currents_nt"] = self.currents.nt
        d["winds_nt"] = self.winds.nt
        d["waves_nt"] = self.waves.nt
        d["currents_dt"] = self.currents.dt
        d["winds_dt"] = self.winds.dt
        d["waves_dt"] = self.waves.dt
        d["currents_n_points"] = self.currents.nx * self.currents.ny
        d["winds_n_points"] = self.winds.nx * self.winds.ny
        d["waves_n_points"] = self.waves.nx * self.waves.ny

        return d

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
            self.nx = 1
            self.ny = 1
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
            self.nx = 1
            self.ny = 1
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
            self.nx = 1
            self.ny = 1
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
