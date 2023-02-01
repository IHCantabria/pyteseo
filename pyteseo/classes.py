from pathlib import Path, PosixPath, WindowsPath

import numpy as np
import pandas as pd

from pyteseo.defaults import DEF_COORDS, DEF_DIRS, DEF_FILES, DEF_VARS
from pyteseo.io.domain import read_coastline, read_grid
from pyteseo.io.forcings import read_2d_forcing, read_cte_forcing, write_null_forcing
from pyteseo.io.results import (
    read_grids_results,
    read_particles_results,
    read_properties_results,
)


class TeseoWrapper:
    def __init__(self, job_path: str):

        path = Path(job_path).resolve()
        if not path.exists():
            path.mkdir(parents=True)

        input_dir = Path(path, DEF_DIRS["inputs"])
        if not input_dir.exists():
            input_dir.mkdir(parents=True)

        self.path = str(path)
        self.input_dir = str(input_dir)

    def load_inputs(self, currents_dt_cte=1, winds_dt_cte=1, waves_dt_cte=1):

        input_dir = Path(self.input_dir).resolve()

        print("Loading grid...")
        if Path(input_dir, DEF_FILES["grid"]).exists():
            self.grid = Grid(Path(input_dir, DEF_FILES["grid"]))
        else:
            raise FileNotFoundError("Grid-file is mandatory!")

        print("Loading coastline...")
        if Path(input_dir, DEF_FILES["coastline"]).exists():
            self.path = Path(input_dir, DEF_FILES["coastline"])
            # TODO - Create Coastline object
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

    def setup(user_parameters):
        pass

    def run(self):
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


class Grid:
    def __init__(self, path: str):
        self.path = str(Path(path).resolve())
        df = read_grid(self.path)
        self.calculate_variables(df)

    def calculate_variables(self, df):
        self.dx = _calculate_dx(df, DEF_COORDS["x"])
        self.dy = _calculate_dy(df, DEF_COORDS["y"])
        self.nx = _calculate_nx(df, DEF_COORDS["x"])
        self.ny = _calculate_ny(df, DEF_COORDS["y"])
        self.x_min = df[DEF_COORDS["x"]].min()
        self.x_max = df[DEF_COORDS["x"]].max()
        self.y_min = df[DEF_COORDS["y"]].min()
        self.y_max = df[DEF_COORDS["y"]].max()

    def __repr__(self) -> str:
        return f"path: '{self.path}'\n dx: {self.dx}\n dy: {self.dy}\n nx: {self.nx}\n ny: {self.ny}\n x_min: {self.x_min}\n x_max: {self.x_max}\n y_min: {self.y_min}\n y_max: {self.y_max}\n"

    def __str__(self) -> str:
        return f"path: '{self.path}'\n dx: {self.dx}\n dy: {self.dy}\n nx: {self.nx}\n ny: {self.ny}\n x_min: {self.x_min}\n x_max: {self.x_max}\n y_min: {self.y_min}\n y_max: {self.y_max}\n"

    @property
    def load(self):
        return read_grid(self.path)


class Coastline:
    def __init__(self, path: str):
        self.path = str(Path(path).resolve())
        df = read_coastline(self.path)
        self.calculate_variables(df)

    def calculate_variables(self, df):
        self.x_min = df[DEF_COORDS["x"]].min()
        self.x_max = df[DEF_COORDS["x"]].max()
        self.y_min = df[DEF_COORDS["y"]].min()
        self.y_max = df[DEF_COORDS["y"]].max()
        self.n_polygons = len(df.index.get_level_values("polygon").unique())

    def __repr__(self) -> str:
        return f"path: '{self.path}'\n n_polygons: {self.n_polygons}\n x_min: {self.x_min}\n x_max: {self.x_max}\n y_min: {self.y_min}\n y_max: {self.y_max}\n"

    def __str__(self) -> str:
        return f"path: '{self.path}'\n n_polygons: {self.n_polygons}\n x_min: {self.x_min}\n x_max: {self.x_max}\n y_min: {self.y_min}\n y_max: {self.y_max}\n"

    @property
    def load(self):
        return read_grid(self.path)


class Currents:
    def __init__(self, lst_path: str | PosixPath | WindowsPath, dt_cte: float = 1.0):
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

            self.dt = _calculate_dt(df, self.varnames["coords"][0])
            self.dx = _calculate_dx(df, self.varnames["coords"][1])
            self.dy = _calculate_dy(df, self.varnames["coords"][2])
            self.nt = _calculate_nt(df, self.varnames["coords"][0])
            self.nx = _calculate_nx(df, self.varnames["coords"][1])
            self.ny = _calculate_ny(df, self.varnames["coords"][2])

    @property
    def load(self):
        if self.dx:
            return read_2d_forcing(self.path, self.forcing_type)
        else:
            return read_cte_forcing(self.path, self.forcing_type, self.dt)


class Winds:
    def __init__(self, lst_path: str | PosixPath | WindowsPath, dt_cte: float = 1.0):
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

            self.dt = _calculate_dt(df, self.varnames["coords"][0])
            self.dx = _calculate_dx(df, self.varnames["coords"][1])
            self.dy = _calculate_dy(df, self.varnames["coords"][2])
            self.nt = _calculate_nt(df, self.varnames["coords"][0])
            self.nx = _calculate_nx(df, self.varnames["coords"][1])
            self.ny = _calculate_ny(df, self.varnames["coords"][2])

    @property
    def load(self):
        if self.dx:
            return read_2d_forcing(self.path, self.forcing_type)
        else:
            return read_cte_forcing(self.path, self.forcing_type, self.dt)


class Waves:
    def __init__(self, lst_path: str | PosixPath | WindowsPath, dt_cte: float = 1.0):
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

            self.dt = _calculate_dt(df, self.varnames["coords"][0])
            self.dx = _calculate_dx(df, self.varnames["coords"][1])
            self.dy = _calculate_dy(df, self.varnames["coords"][2])
            self.nt = _calculate_nt(df, self.varnames["coords"][0])
            self.nx = _calculate_nx(df, self.varnames["coords"][1])
            self.ny = _calculate_ny(df, self.varnames["coords"][2])

    @property
    def load(self):
        if self.dx:
            return read_2d_forcing(self.path, self.forcing_type)
        else:
            return read_cte_forcing(self.path, self.forcing_type, self.dt)


def _calculate_dx(df: pd.DataFrame, coordname: str):
    dx = np.unique(np.diff(df[coordname].unique()))
    if len(dx) == 1:
        return dx[0]
    else:
        print("WARNING: dx is not constant!")
        return dx[0]


def _calculate_dy(df: pd.DataFrame, coordname: str):
    dy = np.unique(np.diff(df[coordname].unique()))
    if len(dy) == 1:
        return dy[0]
    else:
        print("WARNING: dy is not constant!")
        return dy[0]


def _calculate_dt(df: pd.DataFrame, coordname: str):
    dt = np.unique(np.diff(df[coordname].unique()))
    if len(dt) == 1:
        return dt[0]
    else:
        print("WARNING: dt is not constant!")
        return dt[0]


def _calculate_nx(df: pd.DataFrame, coordname: str):
    return len(df[coordname].unique())


def _calculate_ny(df: pd.DataFrame, coordname: str):
    return len(df[coordname].unique())


def _calculate_nt(df: pd.DataFrame, coordname: str):
    return len(df[coordname].unique())
