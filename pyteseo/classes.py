from pathlib import Path, PosixPath, WindowsPath
import numpy as np

from pyteseo.defaults import DEF_COORDS, DEF_DIRS, DEF_FILES
from pyteseo.io.forcings import (
    read_2d_forcings,
    read_cte_forcings,
    # write_cte_currents,
    # write_cte_winds,
    # write_cte_waves,
)

from pyteseo.io.domain import read_grid


class TeseoWrapper:
    def __init__(self, job_path: str | PosixPath | WindowsPath):

        path = Path(job_path).resolve()
        if not path.exists():
            path.mkdir(parents=True)

        input_dir = Path(path + DEF_DIRS["inputs"])
        if not input_dir.exists():
            input_dir.mkdir(parents=True)

        self.path = str(path)
        self.input_dir = str(input_dir)
        self.load_inputs()

    def load_inputs(self, input_dir):

        input_dir = Path(input_dir).resolve()

        if Path(input_dir, DEF_FILES["grid"]).exists():
            self.grid = TeseoGrid(input_dir)
        else:
            self.grid = None

        if Path(input_dir, DEF_FILES["currents"]).exists():
            self.currents = TeseoCurrents(input_dir)
        else:
            self.currents = None

        if Path(input_dir, DEF_FILES["winds"]).exists():
            self.winds = TeseoWinds(input_dir)
        else:
            self.winds = None

        if Path(input_dir, DEF_FILES["waves"]).exists():
            self.waves = TeseoWaves(input_dir)
        else:
            self.waves = None

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
        self.dx = _calculate_dx(df)
        self.dy = _calculate_dy(df)
        self.nx = _calculate_nx(df)
        self.ny = _calculate_ny(df)

    @property
    def load(self):
        return read_grid(self.path)


class TeseoCurrents:
    def __init__(
        self, path: str | PosixPath | WindowsPath, dt_cte: float | None = None
    ):
        self.type = "currents"
        self.varnames = ["time", "lon", "lat", "u", "v"]
        self.path = str(Path(path).resolve())

        if dt_cte:
            df = read_cte_forcings(self.path, self.varnames[3:])
            self.dx = None
            self.dy = None
            self.dt = dt_cte
            self.nx = None
            self.ny = None
            self.nt = len(df)

        else:
            df = read_2d_forcings(self.path, self.varnames[1:])

            self.dx = _calculate_dx(df)
            self.dy = _calculate_dy(df)
            self.dt = _calculate_dt(df)
            self.nx = _calculate_nx(df)
            self.ny = _calculate_ny(df)
            self.nt = _calculate_nt(df)

    @property
    def load(self):
        if self.dx:
            return read_2d_forcings(self.path, self.varnames[1:])
        else:
            return read_cte_forcings(self.path, self.varnames[3:])


class TeseoWinds:
    def __init__(self, path: str | PosixPath | WindowsPath):
        self.type = "winds"
        self.file_columns = ["lon", "lat", "u", "v"]
        self.path = str(Path(path).resolve())

        df = read_2d_forcings(self.path, self.file_columns)

        self.dx = _calculate_dx(df)
        self.dy = _calculate_dy(df)
        self.dt = _calculate_dt(df)
        self.nx = _calculate_nx(df)
        self.ny = _calculate_ny(df)
        self.nt = _calculate_nt(df)

    @property
    def load(self):
        return read_2d_forcings(self.path, self.vars)


class TeseoWaves:
    def __init__(self, path: str | PosixPath | WindowsPath):
        self.type = "waves"
        self.file_columns = ["lon", "lat", "hs", "tp", "dir"]
        self.path = str(Path(path).resolve())

        df = read_2d_forcings(self.path, self.file_columns)

        self.dx = _calculate_dx(df)
        self.dy = _calculate_dy(df)
        self.dt = _calculate_dt(df)
        self.nx = _calculate_nx(df)
        self.ny = _calculate_ny(df)
        self.nt = _calculate_nt(df)

    @property
    def load(self):
        return read_2d_forcings(self.path, self.vars)


def _calculate_dx(df, coordname: str = DEF_COORDS["x"]):
    dx = np.unique(np.diff(df[coordname].unique()))
    if len(dx) == 1:
        return dx[0]
    else:
        print("WARNING: dx is not constant!")
        return dx[0]


def _calculate_dy(df, coordname: str = DEF_COORDS["y"]):
    dy = np.unique(np.diff(df[coordname].unique()))
    if len(dy) == 1:
        return dy[0]
    else:
        print("WARNING: dy is not constant!")
        return dy[0]


def _calculate_dz(df, coordname: str = DEF_COORDS["z"]):
    dz = np.unique(np.diff(df[coordname].unique()))
    if len(dz) == 1:
        return dz[0]
    else:
        print("WARNING: dz is not constant!")
        return dz[0]


def _calculate_dt(df, coordname: str = DEF_COORDS["t"]):
    dt = np.unique(np.diff(df[coordname].unique()))
    if len(dt) == 1:
        return dt[0]
    else:
        print("WARNING: dt is not constant!")
        return dt[0]


def _calculate_nx(df, coordname: str = DEF_COORDS["x"]):
    return len(df[coordname].unique())


def _calculate_ny(df, coordname: str = DEF_COORDS["y"]):
    return len(df[coordname].unique())


def _calculate_nz(df, coordname: str = DEF_COORDS["z"]):
    return len(df[coordname].unique())


def _calculate_nt(df, coordname: str = DEF_COORDS["t"]):
    return len(df[coordname].unique())
