import subprocess
from pathlib import Path
from shutil import copyfile

from pyteseo.classes import Coastline, Currents, Grid, Waves, Winds
from pyteseo.defaults import (
    CFG_MAIN_MANDATORY_KEYS,
    CFG_SPILL_POINT_MANDATORY_KEYS,
    DIRECTORY_NAMES,
    FILE_NAMES,
    FILE_PATTERNS,
)
from pyteseo.io.cfg import generate_parameters_for_cfg, write_cfg
from pyteseo.io.forcings import write_null_forcing
from pyteseo.io.results import (
    read_grids_results,
    read_particles_results,
    read_properties_results,
)
from pyteseo.io.run import complete_run_default_parameters, write_run


class TeseoWrapper:
    def __init__(self, dir_path: str, simulation_keyword: str = "teseo"):
        """wrapper of configuration, execution and postprocess of a TESEO's simulation

        Args:
            path (str): path to the simulation folder
            simulation_keyword (str, optional): keyword to name simulation files. Defaults to "teseo".
        """
        print("\n")
        self.simulation_keyword = simulation_keyword
        self.path = str(Path(dir_path).resolve())
        self.create_folder_structure()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"

    def create_folder_structure(self):
        """creates folder structure for TESEO simulation"""
        print("Creating TESEO folder structure...")
        path = Path(self.path)
        if not path.exists():
            path.mkdir(parents=True)

        input_dir = Path(path, DIRECTORY_NAMES["input"])
        if not input_dir.exists():
            input_dir.mkdir(parents=True)

        output_dir = Path(path, DIRECTORY_NAMES["output"])
        if not output_dir.exists():
            output_dir.mkdir(parents=True)

        self.input_dir = str(input_dir)
        self.output_dir = str(output_dir)
        print(f"DONE! Created @ {self.path}\n")

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
        if Path(input_dir, FILE_NAMES["grid"]).exists():
            self.grid = Grid(Path(input_dir, FILE_NAMES["grid"]))
        else:
            raise FileNotFoundError("Grid-file is mandatory!")

        print("Loading coastline...")
        if Path(input_dir, FILE_NAMES["coastline"]).exists():
            self.coastline = Coastline(Path(input_dir, FILE_NAMES["coastline"]))
        else:
            print("No coastline defined!")

        print("Loading currents...")
        if Path(input_dir, FILE_NAMES["currents"]).exists():
            self.currents = Currents(
                Path(input_dir, FILE_NAMES["currents"]), currents_dt_cte
            )
        else:
            print("No currents defined, creating null currents...")
            self.currents = None
            write_null_forcing(input_dir, forcing_type="currents")

        print("Loading winds...")
        if Path(input_dir, FILE_NAMES["winds"]).exists():
            self.winds = Winds(Path(input_dir, FILE_NAMES["winds"]), winds_dt_cte)
        else:
            print("No winds defined, creating null winds...")
            self.winds = None
            write_null_forcing(input_dir, forcing_type="winds")

        print("Loading waves...")
        if Path(input_dir, FILE_NAMES["waves"]).exists():
            self.waves = Waves(Path(input_dir, FILE_NAMES["waves"]), waves_dt_cte)
        else:
            print("No waves defined, creating null waves...")
            self.waves = None
            write_null_forcing(input_dir, forcing_type="waves")
        print("DONE!\n")

    def setup(self, user_parameters: dict[str, any]):
        """create TESEO's configuration files (*.cfg and *.run)

        Args:
            user_parameters (dict[str, any]): parameters definde by the user to configure the simulation
        """
        check_user_minimum_parameters(user_parameters)
        print("setting up TESEO's cfg-file...")
        cfg_parameters = generate_parameters_for_cfg(user_parameters)
        forcing_parameters = self._forcing_parameters
        file_parameters = self._file_parameters

        self.cfg_path = str(
            Path(self.path, FILE_PATTERNS["cfg"].replace("*", self.simulation_keyword))
        )
        write_cfg(
            output_path=self.cfg_path,
            filename_parameters=file_parameters,
            forcing_parameters=forcing_parameters,
            simulation_parameters=cfg_parameters,
        )
        print("cfg-file created\n")
        print("setting up TESEO's cfg-file...")
        if "first_time_saved" not in user_parameters.keys():
            first_time_saved = min(
                [
                    spill_point["release_time"]
                    for spill_point in cfg_parameters["spill_points"]
                ]
            )

        run_parameters = complete_run_default_parameters(user_parameters)
        n_coastal_polygons = self.coastline.n_polygons
        self.run_path = str(
            Path(self.path, FILE_PATTERNS["run"].replace("*", self.simulation_keyword))
        )
        write_run(
            path=self.run_path,
            run_parameters=run_parameters,
            first_time_saved=first_time_saved,
            n_coastal_polygons=n_coastal_polygons,
        )
        print("run-file created\n")

    def run(self):
        """run TESEO simulation"""
        self.prepare_teseo_binary()
        self.check_files()
        self.execute_simulation()

    def check_files(self):
        """check minimum files required

        Raises:
            FileNotFoundError: If required file is not found
        """
        for path in [
            self.grid.path,
            self.path,
            self.input_dir,
            self.cfg_path,
            self.run_path,
        ]:
            if not Path(path).exists():
                raise FileNotFoundError(path)

    def prepare_teseo_binary(self, teseo_binary_path: str):
        """copy teseo binary to the simulation folder

        Args:
            teseo_binary_path (str): path to the binary of TESEO

        Raises:
            FileNotFoundError: if the file is not found
        """
        self.teseo_binary_path = Path(self.path, Path(teseo_binary_path).name)
        if Path(teseo_binary_path).exists():
            copyfile(teseo_binary_path, self.teseo_binary_path)
        else:
            raise FileNotFoundError(teseo_binary_path)

    def execute_simulation(self):
        """triggers the simulation using subprocess"""
        subprocess.run(
            [f"{self.teseo_binary_path} {self.cfg_path}"], cwd=self.path, check=True
        )

    @property
    def load_particles(self):
        read_particles_results(self.path)

    @property
    def load_properties(self):
        read_properties_results(self.path)

    @property
    def load_grids(self):
        read_grids_results(self.path)

    @property
    def _file_parameters(self) -> dict:
        d = {}
        d["inputs_directory"] = DIRECTORY_NAMES["input"] + "/"
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


def check_user_minimum_parameters(
    user_parameters,
    cfg_mandatory_keys=CFG_MAIN_MANDATORY_KEYS,
    cfg_spill_point_mandatory_keys=CFG_SPILL_POINT_MANDATORY_KEYS,
):
    check_keys(d=user_parameters, mandatory_keys=cfg_mandatory_keys)
    for spill_point in user_parameters["spill_points"]:
        if user_parameters["substance_type"] in ["oil", "hns"]:
            check_keys(
                d=spill_point,
                mandatory_keys=cfg_spill_point_mandatory_keys
                + ["substance", "mass", "thickness"],
            )
        else:
            check_keys(d=spill_point, mandatory_keys=cfg_spill_point_mandatory_keys)


def check_keys(d, mandatory_keys):
    for key in mandatory_keys:
        if key not in d.keys():
            raise KeyError(f"Mandatory parameter [{key}] not found")
