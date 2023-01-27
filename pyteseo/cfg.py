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
from pyteseo.io import write_cte_currents, write_cte_waves, write_cte_winds


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


# FIXME - for new TESEO v2.0.0:
# 1. format .csv for all the input
# 2. domain_grid_path = /absolute_path/grid.csv                                         [lon, lat, depth]
# 3. results_grid_path = /absolute_path/results_grid.csv                                [lon, lat, (depth)]
# 4. coastline_path = /absolute_path/coastline.csv [polygon_id, lon, lat]
# 5. quitar flag linea de costa adhiere si/no. si declaramos archivo adhiere, sino no!
# 6. definicion de forcings currents_list = /absolute_path/currents.csv                 [path]
#     cte en el espacio --> currents = /absolute_path/cte_currents.csv                  [time, lon, lat, u, v, (w)]
#     winds y waves igual                                                               [time, lon, lat, hs, tp, dir]
# 7. definir initial_datetime = [2023, 1, 1, 0, 0, 0]  --> datetime lib for fortran

# grid [path]
# coastline [adherence, mode, algorithm]
# processes [spreading[hours, type], ]
# forcings [currents[nt, dt, nx*ny], winds[nt, dt, nx*ny], waves[nt, dt, nx*ny]]
# simulation[type, dim, duration, dt]


def write_cfg(input_parameters, forcings_parameters, cfg_parameters, output_path):

    cfg_txt = f"""* FICHERO DE CONFIGURACIÓN PARA Modelo TESEO (FUEL-FLOTANTES-HNS, 2D-3D)
*--------------------------------------------------
* MALLA:
*--------------------------------------------------
* Nombre_malla
{cfg_parameters["grid_name"]}
* Tipo malla(1:xyz; 2:grid)
{1}
* Origen_x(°) Origen_y(°) Delta_x(°) Delta_y(°) Delta_z Celda_x Celda_y Celda_z LatMedia
{0} {0} {0} {0} {0} {0} {0} {0} {0}
*-------------------------------------------------------------------------------------
* MALLA DE PROBABILIDADES o CONCENTRACIONES: (SI GRABA_CONC=1)
*--------------------------------------------------------------------------------------
* Nombre_malla
{cfg_parameters["grid_name"]}
* MALLA_CONCS.VS.MALLA_MODELO (0:Malla_concs.NE.Malla_modelo; 1:Malla_concs.EQ.Malla_modelo)
{0}
* Tipo malla(1:xyz; 2:grid)
{1}
* IF Tipo malla=2: Origen_x(°) Origen_y(°) Delta_x(°) Delta_y(°) Delta_z Celda_x Celda_y Celda_z LatMedia
{0} {0} {0} {0} {0} {0} {0} {0} {0}
*--------------------------------------------------
* LINEA DE COSTA:
*--------------------------------------------------
* Linea de costa con indice adhiere/no adhiere (0:NO;1:SI) [Si 0 en punto costa.dat ADHIERE, si 1 en punto costa.dat NO-ADHIERE]
{cfg_parameters["coastline_adherence_flag"]}
*--------------------------------------------------
* VERTIDO:
*--------------------------------------------------
* TIPO_DE_VERTIDO_FLOTANTE(1)_FUEL(2)_HNS(3)
{input_parameters["spill_type"]}
* SIMULO_SPREADING(0:NO;1:SI) ALGORTIMO_SPREADING((1=ALG_DIF.EQUIVALENTE[ADIOS2],2=ALG_ELIPSOIDAL[LEHR],3=ALG_RABEH-KOLLURU[MOHID-HNS])) TIEMPO_PARADA_SPREADING_CUANDO_FUEL (horas)
{cfg_parameters["spreading_flag"]}    {cfg_parameters["spreading_type"]}    {cfg_parameters["spreading_fuel_hours"]}
* SIMULO_EVAPORACION(0:NO;1:SI)****SOLO_SI_TIPO_DE_VERTIDO=2 y 3
{cfg_parameters["evaporation_flag"]}
* SIMULO_EMULSIONADO(0:NO;1:SI)****SOLO_SI_TIPO_DE_VERTIDO=2
{cfg_parameters["emulsification_flag"]}
* SIMULO DISPERSIÓN VERTICAL (ENTRAINMENT) = 0:NO; 1:SÍ ****SOLO_SI_TIPO_DE_VERTIDO=2 y 3
{cfg_parameters["vertical_dispersion_flag"]}
* SIMULO_DISOLUCION VOLATILIZACION SEDIMENTACION BIODEGRADACION_LARGOPLAZO (0:NO;1:SI)****SOLO_SI_TIPO_DE_VERTIDO=3
{cfg_parameters["dissolution_flag"]}   {cfg_parameters["volatilization_flag"]}   {cfg_parameters["sedimentation_flag"]}    {cfg_parameters["biodegradation_flag"]}
* VISC_CINEMATICA_AGUA_MAR(m2/s)
{cfg_parameters["sea_kinematic_visc"]}
* Datos de vertidos:
* VERTIDO INSTANTANEO(1) O CONTINUO-3D(2)
{input_parameters["release_type"]}
* SI VERTIDO INSTANTANEO: Nº_PUNTOS_DE_VERTIDO
{input_parameters["spill_points"]}
* SI VERTIDO CONTINUO-3D: DURACION VERTIDO (horas) DT_PULSOS(segundos - Indicaciones: número divisible de la duración del vertido y mayor y múltiplo del paso de tiempo de cálculo --> Si es mayor que DT_PARTS definido en .run, se toma DT_PARTS-es valor máximo para que no haya saltos en graficado))
* A tener en cuenta: cuanto menor es el DT_PULSOS, mayor será el tiempo de cómputo ya que se introducen más partículas en el medio
{input_parameters["release_duration_h"]}   {input_parameters["release_dt_s"]}
* PROPIEDADES VERTIDO/MEDIO
* ID T_inicio Masa   Coord_x  Coord_y   z   Ancho_x Ancho_y Espesor EspMin Volum_TOT    TIPO_FUEL       DENS  TEMP_D0 VISC_K TEMP_V0 WATER_SOLUBILITY  TEMP_SOL  VAPOUR_PRESS TEMP_VP  MOL_WEIGHT  ORGANIC EVAP_MAX EVAP_MIN EMULS_MAX  DENSIDAD_MAR  TEMP_MAR TEMP_AIR
*      (h)    (Kg)     (°)      (°)  (si 3D)(en sup)(en sup)  (OIL)    (m)   M/D(m3)      (OIL)        (kg/m3) (ºC)   (cSt)   (ºC)       (SI NHS)        (ºC)      (SI NHS)     (ºC)    (kg/kmol) (SI NHS)   (%)      (%)     (OIL)       (kg/m3)      (ºC)    (ºC)
*      (h)    (Kg)     (°)     (°)    (m)    (m)     (m)      (m)     (m)   M/D(m3) CRUDO=0/REFINADO=1 (kg/m3) (ºC)   (cSt)   (ºC)   (mg/L)(max10E7)    (ºC)       (KPa)       (ºC)    (kg/kmol)   1:SI     (%)      (%)      (%)        (kg/m3)      (ºC)    (ºC)
{input_parameters["spill_table"]}
* PROPIEDADES EXTRA VERTIDO/MEDIO SI TIPO_DE_VERTIDO es 3 (HNS)  [TANTAS LINEAS COMO PUNTOS DE VERTIDO]
* ID  ConcentracionSS  Sorption_coef(LogKoc)  Degrad_rate
*	    (Si HNS)			(Si HNS)		   (Si HNS)
*	     (mg/L)				 (-)  			   (day-1)
{input_parameters["hns_table"]}
*--------------------------------------------------
* SIMULACION NUMERICA:
*--------------------------------------------------
* TIEMPO_TOTAL(h)
{input_parameters["total_hours"]}
*
* FORZAMIENTOS:
*--------------------------------------------------
***
* CORRIENTES:
* CORRIENTES_POR_FICHERO(1)_O_FIJO(2) Tipo_Malla(1=regular,0=irregular) Tipo_Dato(0=MallaConstante,1=MallaVariable) ModoVariable(1=MojoSeco,2=Radar)
* MODIFICACION_CORRIENTES_POR_PARÁMETROS_EXTERNOS(0:NO;1:SI)!_SIEMPRE_QUE_CORRIENTES_SEAN_POR_FICHERO Us_Vs_(Ws)_mismo_file(0=No,1=Sí)
{2 if forcings_parameters["n_files_currents"] == 0 else 1} {1} {0} {1} {0} {1}
* SI_VERTIDO_3D_CORRIENTES_COLUMNA_POR_CAPAS(1)_O_PROMEDIADAS_EN_VERTICAL-zonaXYVertido(2)****OPCIÓN PROMEDIADAS_EN_VERTICAL(2) de momento SOLO_SI_CORRIENTES_POR_FICHERO, Tipo_Malla_Regular, Tipo_Dato_MallaConstante, Us_Vs_mismo_file(sin Ws), interpolaciones 0
{2}
* FORMATO MALLA  FORMATO MALLA_PARCORRECTOR [(1:xyz; 2:grid)] [NOTA:GRID PARA CORRIENTES EN MALLA REGULAR Y DATOS POR FICHERO]
{1} {2}
* TIEMPO_ENTRE_FICHEROS(h) Nº_DE_FICHEROS_O_DE_LINEAS_DE_LA_TABLA  Nº_DE_FICHEROS_CORRECTORES(=_Nº_FICHEROS_CORRIENTES)
{forcings_parameters["dt_currents"]}   {forcings_parameters["n_files_currents"]}    {forcings_parameters["n_files_currents"]}
* SI_FORMATO_MALLA=1 O FORMATO_MALLACORRECTOR=1::Nº_NODOS_U  Nº_NODOS_V  Nº_NODOS_W
{forcings_parameters["n_nodes_currents"]}    {forcings_parameters["n_nodes_currents"]}    {forcings_parameters["n_nodes_currents"]}
* SI_FORMATO_MALLA=2 O FORMATO_MALLACORRECTOR=2 LEER::
* COMPONENTE_U: ORIGEN_X(°) ORIGEN_Y(°) DELTA_X(°) DELTA_Y(°) CELDA_X CELDA_Y
{0} {0} {0} {0} {0} {0}
* COMPONENTE_V: ORIGEN_X(°) ORIGEN_Y(°) DELTA_X(°) DELTA_Y(°) CELDA_X CELDA_Y
{0} {0} {0} {0} {0} {0}
***
* OLEAJE:
* OLEAJE_POR_FICHERO(1)_O_FIJO(2-m,º,s)  Tipo_Malla(1=regular,0=irregular)
{2 if forcings_parameters["n_files_waves"] == 0 else 1}  {1}
* FORMATO MALLA(1:xyz; 2:grid)
{1}
* TIEMPO_ENTRE_FICHEROS(h); Nº_DE_FICHEROS_O_DE_LINEAS_DE_LA_TABLA
{1}  {1}
* SI_FORMATO_MALLA=1:: Nº_DE_PUNTOS (HS_T_y_Dir_en_el_mismo_fichero)
{0}
* SI_FORMATO_MALLA=2:: ORIGEN_X(°) ORIGEN_Y(°) DELTA_X(°) DELTA_Y(°) CELDA_X CELDA_Y [Variables_en_ficheros_individuales]
{0} {0} {0} {0} {0} {0}
***
* VIENTO:
* VIENTO_POR_FICHERO(1)_O_FIJO(2-m/s,º) Tipo_Malla(1=regular,0=irregular)
{2 if forcings_parameters["n_files_winds"] == 0 else 1}  {1}
* FORMATO MALLA(1:xyz; 2:grid)
{1}
* TIEMPO_ENTRE_FICHEROS(h) Nº_DE_FICHEROS_O_DE_LINEAS_DE_LA_TABLA
{1 if forcings_parameters["dt_winds"] == 0 else forcings_parameters["dt_winds"]}  {1 if forcings_parameters["n_files_winds"] == 0 else forcings_parameters["n_files_winds"]}
* SI_FORMATO_MALLA=1:: Nº_DE_PUNTOS (Uw_y_Vw_en_el_mismo_fichero)
{forcings_parameters["n_nodes_winds"]}
* SI_FORMATO_MALLA=2:: ORIGEN_X(°) ORIGEN_Y(°) DELTA_X(°) DELTA_Y(°) CELDA_X CELDA_Y [Variables_en_ficheros_individuales]
{0} {0} {0} {0} {0} {0}
* FACTORES (4 PRIMERAS COLUMNAS) | DIFUSION (3 RESTANTES) [TANTAS LINEAS COMO PUNTOS DE VERTIDO]
*--------------------------------------------------
* FACTOR_CURRENTS CD_VIENTO(0.03-0.05):ALFA	 CD_VIENTO:BETA  FACTOR_OLEAJE  DISPERSION(0:NO,1:SI)  D   KZ(m2/s)[0.01 sobre 30 m:DeDominicis2013]_(K1,2=D;K3=KZ->SIEMPRE QUE MEDIO_EJECUCION=1) S(Pdte_supf_agua-> SIEMPRE QUE MEDIO_EJECUCION=2)
{input_parameters["coefficients_table"]}
*--------------------------------------------------
* DIRECTORIO DATOS:
*------------------------------------------------------
* SI DIRECTORIO_DATOS_EJECUCION_MODELO=2 -> AÑADIR NUEVA RUTA(); SI DIRECTORIO=1->AÑADIR la ruta no cambia
{cfg_parameters["input_dir"]}
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cfg_txt)

    return output_path


def write_run(dir_path):
    print("doing something...")


# def read_cfg(path):
#     print("doing something...")


# def read_run(path):
#     print("doing something...")
