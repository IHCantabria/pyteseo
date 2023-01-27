from pathlib import Path, PosixPath, WindowsPath
import numpy as np
import pandas as pd

from pyteseo.defaults import DEF_COORDS, DEF_DIRS, DEF_FILES
from pyteseo.io.forcings import (
    read_currents,
    read_winds,
    read_waves,
    write_cte_currents,
    write_cte_winds,
    write_cte_waves,
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
        # self.auto_load_parameters()

    def load_inputs(self, input_dir):

        input_dir = Path(input_dir).resolve()

        self.grid = get_grid(input_dir)
        self.coastline = get_coastline(input_dir)
        self.currents = get_currents(input_dir)
        self.winds = get_winds(input_dir)

        self.write_non_used_forcings()

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

    def write_non_used_forcings(self):
        if not self.currents:
            zero_df = pd.DataFrame({"time": [0], "u": [0], "v": [0]})
            write_cte_currents(df=zero_df, dir_path=self.input_dir)

        if not self.winds:
            zero_df = pd.DataFrame({"time": [0], "u": [0], "v": [0]})
            write_cte_winds(df=zero_df, dir_path=self.input_dir)

        if not self.waves:
            zero_df = pd.DataFrame({"time": [0], "hs": [0], "tp": [0], "dir": [0]})
            write_cte_waves(df=zero_df, dir_path=self.input_dir)


def get_grid(dir_path: str | PosixPath | WindowsPath):
    path = Path(dir_path, DEF_FILES["grid"])
    if path.exists():
        return TeseoGrid(path)
    else:
        print("WARNING: No grid founded!")
        return None


def get_coastline(dir_path: str | PosixPath | WindowsPath):
    path = Path(dir_path, DEF_FILES["coastline"])
    if path.exists():
        # TODO return TeseoCoastline(path)
        print("WARNING: No coastline founded!")
        return None
    else:
        print("WARNING: No coastline founded!")
        return None


def get_currents(dir_path: str | PosixPath | WindowsPath):
    path = Path(dir_path, DEF_FILES["currents_list"])
    if path.exists():
        return TeseoCurrents(path)
    else:
        print("WARNING: No currents founded!")
        return None


def get_winds(dir_path: str | PosixPath | WindowsPath):
    path = Path(dir_path, DEF_FILES["winds_list"])
    if path.exists():
        return TeseoWinds(path)
    else:
        print("WARNING: No winds founded!")
        return None


def get_waves(dir_path: str | PosixPath | WindowsPath):
    path = Path(dir_path, DEF_FILES["waves_list"])
    if path.exists():
        # TODO return TeseoWaves(path)
        print("WARNING: No waves founded!")
        return None
    else:
        print("WARNING: No waves founded!")
        return None


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
    def __init__(self, path: str | PosixPath | WindowsPath):
        self.type = "currents"
        self.path = str(Path(path).resolve())
        df = read_currents(self.path)
        self.dx = _calculate_dx(df)
        self.dy = _calculate_dy(df)
        self.dt = _calculate_dt(df)
        self.nx = _calculate_nx(df)
        self.ny = _calculate_ny(df)
        self.nt = _calculate_nt(df)

    @property
    def load(self):
        return read_currents(self.path)


class TeseoWinds:
    def __init__(self, path: str | PosixPath | WindowsPath):
        self.type = "winds"
        self.path = str(Path(path).resolve())
        df = read_winds(self.path)
        self.dx = _calculate_dx(df)
        self.dy = _calculate_dy(df)
        self.dt = _calculate_dt(df)
        self.nx = _calculate_nx(df)
        self.ny = _calculate_ny(df)
        self.nt = _calculate_nt(df)

    @property
    def load(self):
        return read_winds(self.path)


class TeseoWaves:
    def __init__(self, path: str | PosixPath | WindowsPath):
        self.type = "waves"
        self.path = str(Path(path).resolve())
        df = read_waves(self.path)
        self.dx = _calculate_dx(df)
        self.dy = _calculate_dy(df)
        self.dt = _calculate_dt(df)
        self.nx = _calculate_nx(df)
        self.ny = _calculate_ny(df)
        self.nt = _calculate_nt(df)

    @property
    def load(self):
        return read_waves(self.path)


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
