from pathlib import Path

import numpy as np
import pandas as pd

from pyteseo.defaults import COORDINATE_NAMES, VARIABLE_NAMES
from pyteseo.io.domain import read_coastline, read_grid
from pyteseo.io.forcings import read_2d_forcing, read_cte_forcing


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
        self.x_min = df[COORDINATE_NAMES["x"]].min()
        self.x_max = df[COORDINATE_NAMES["x"]].max()
        self.y_min = df[COORDINATE_NAMES["y"]].min()
        self.y_max = df[COORDINATE_NAMES["y"]].max()

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
        self.x_min = df[COORDINATE_NAMES["x"]].min()
        self.x_max = df[COORDINATE_NAMES["x"]].max()
        self.y_min = df[COORDINATE_NAMES["y"]].min()
        self.y_max = df[COORDINATE_NAMES["y"]].max()
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
        self.varnames = VARIABLE_NAMES[self.forcing_type]
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
        self.varnames = VARIABLE_NAMES[self.forcing_type]
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
        self.varnames = VARIABLE_NAMES[self.forcing_type]
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


def _calculate_dx(df: pd.DataFrame, coordname: str = COORDINATE_NAMES["x"]):
    dx = np.unique(np.diff(df[coordname].unique()))
    if len(dx) == 1:
        return dx[0]
    else:
        print("WARNING: dx is not constant!")
        return dx[0]


def _calculate_dy(df: pd.DataFrame, coordname: str = COORDINATE_NAMES["y"]):
    dy = np.unique(np.diff(df[coordname].unique()))
    if len(dy) == 1:
        return dy[0]
    else:
        print("WARNING: dy is not constant!")
        return dy[0]


def _calculate_dt(df: pd.DataFrame, coordname: str = COORDINATE_NAMES["t"]):
    dt = np.unique(np.diff(df[coordname].unique()))
    if len(dt) == 1:
        return dt[0]
    else:
        print("WARNING: dt is not constant!")
        return dt[0]


def _calculate_nx(df: pd.DataFrame, coordname: str = COORDINATE_NAMES["x"]):
    return len(df[coordname].unique())


def _calculate_ny(df: pd.DataFrame, coordname: str = COORDINATE_NAMES["y"]):
    return len(df[coordname].unique())


def _calculate_nt(df: pd.DataFrame, coordname: str = COORDINATE_NAMES["t"]):
    return len(df[coordname].unique())
