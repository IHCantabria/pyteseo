from pathlib import Path, PosixPath, WindowsPath
import numpy as np
import pandas as pd

from pyteseo.defaults import DEF_DIRS, DEF_FILES, DEF_VARS, DEF_COORDS
from pyteseo.io.forcings import read_2d_forcing, read_cte_forcing, write_null_forcing
from pyteseo.io.domain import read_grid


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

        if Path(input_dir, DEF_FILES["grid"]).exists():
            self.grid = TeseoGrid(Path(input_dir, DEF_FILES["grid"]))
        else:
            raise ValueError("No grid-file in the input directory")

        if Path(input_dir, DEF_FILES["currents"]).exists():
            self.currents = TeseoCurrents(
                Path(input_dir, DEF_FILES["currents"]), currents_dt_cte
            )
        else:
            self.currents = None
            write_null_forcing(input_dir, forcing_type="currents")

        if Path(input_dir, DEF_FILES["winds"]).exists():
            self.winds = TeseoWinds(Path(input_dir, DEF_FILES["winds"]), winds_dt_cte)
        else:
            self.winds = None
            write_null_forcing(input_dir, forcing_type="winds")

        if Path(input_dir, DEF_FILES["waves"]).exists():
            self.waves = TeseoWaves(Path(input_dir, DEF_FILES["waves"]), waves_dt_cte)
        else:
            self.waves = None
            write_null_forcing(input_dir, forcing_type="waves")

    def setup(user_parameters):
        pass

    def run(self):
        pass

    @property
    def particles():
        pass
        # return df

    @property
    def properties():
        pass
        # return df

    @property
    def grids():
        pass
        # return df


class TeseoGrid:
    def __init__(self, path: str | PosixPath | WindowsPath):

        self.type = "domain_grid"
        self.path = str(Path(path).resolve())
        df = read_grid(self.path)
        self.dx = _calculate_dx(df, DEF_COORDS["x"])
        self.dy = _calculate_dy(df, DEF_COORDS["y"])
        self.nx = _calculate_nx(df, DEF_COORDS["x"])
        self.ny = _calculate_ny(df, DEF_COORDS["y"])

    @property
    def load(self):
        return read_grid(self.path)


class TeseoCurrents:
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


class TeseoWinds:
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


class TeseoWaves:
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
