from datetime import datetime

import pandas as pd

from pyteseo.defaults import (
    CFG_KEYS_FOR_TABLE_1,
    CFG_KEYS_FOR_TABLE_2,
    CFG_KEYS_FOR_TABLE_3,
    CFG_MAIN_PARAMETERS,
    CFG_PROCESSES_PARAMETERS,
    CFG_SPILL_POINT_PARAMETERS,
)
from pyteseo.io.substances import import_local
from pyteseo.io.utils import _add_default_parameters

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


def generate_parameters_for_cfg(user_parameters: dict) -> dict:
    """generates parameters needed to fullfil TESEO's cfg-file

    Args:
        user_parameters (dict): Parameters defined by the user

    Returns:
        dict: parameters needed to fullfil cfg-file
    """

    CFG_MAIN_PARAMETERS.update(
        CFG_PROCESSES_PARAMETERS[user_parameters["substance_type"]]
    )

    cfg_parameters = _add_default_parameters(user_parameters, CFG_MAIN_PARAMETERS)

    cfg_parameters["spill_points"] = add_spill_point_default_parameters(
        cfg_parameters["spill_points"]
    )

    cfg_parameters["spill_points"] = add_hours_to_release_to_spill_points(
        cfg_parameters["spill_points"], cfg_parameters["forcing_init_datetime"]
    )

    return cfg_parameters


def add_hours_to_release_to_spill_points(
    spill_points: list[dict], forcing_init_datetime: datetime
) -> list[dict]:
    """add parameter 'hours_to_release' as the difference between the 'forcing init time' and the 'release time' of each spill point

    Args:
        spill_points (list[dict]): list of spill point definitions
        forcing_init_datetime (datetime): initial time of the forcings (real initial reference time of TESEO's simulations)

    Returns:
        list[dict]: spill_points updated with 'hours_to_release'
    """
    for i, d in enumerate(spill_points):
        d["hours_to_release"] = (
            d["release_time"] - forcing_init_datetime
        ).total_seconds() / 3600
        spill_points[i] = d

    return spill_points


def add_spill_point_default_parameters(
    spill_points: list[dict], d_defaults: dict[str, any] = CFG_SPILL_POINT_PARAMETERS
) -> list[dict]:
    """complete spill point definitions with default parameters

    Args:
        spill_points (list[dict]): spill point definitions
        d_defaults (dict[str, any], optional): defaults to be added. Defaults to CFG_SPILL_POINT_PARAMETERS.

    Returns:
        list[dict]: spill_points updated with the defaults passed in 'd_defaults'
    """
    for i, d in enumerate(spill_points):
        spill_points[i] = _add_default_parameters(d, d_defaults)

    return spill_points


def write_cfg(
    output_path: str,
    filename_parameters: dict[str, str],
    forcing_parameters: dict[str, any],
    simulation_parameters: dict[str, any],
):
    """create f-string with the complete TESEO's cfg-file

    Args:
        output_path (str): path to write the file
        filename_parameters (dict[str, str]): filenames required
        forcing_parameters (dict[str, any]): forcings parameters required
        simulation_parameters (dict[str, any]): rest of parameters required
    """
    release_type = translate_release_type(simulation_parameters["release_type"])
    substance_type = translate_substance_type(simulation_parameters["substance_type"])
    spreading_formulation = translate_spreading_formulation(
        simulation_parameters["spreading_formulation"]
    )

    table1, table2, table3 = create_tables(
        simulation_parameters["spill_points"],
        simulation_parameters["substance_type"],
        simulation_parameters["seawater_temperature"],
        simulation_parameters["seawater_density"],
        simulation_parameters["air_temperature"],
        simulation_parameters["suspended_solid_concentration"],
    )

    cfg_txt = f"""* FICHERO DE CONFIGURACIÓN PARA Modelo TESEO (FUEL-FLOTANTES-HNS, 2D-3D)
*--------------------------------------------------
* MALLA:
*--------------------------------------------------
* Nombre_malla
{filename_parameters["grid_filename"]}
* Tipo malla(1:xyz; 2:grid)
{1}
* Origen_x(°) Origen_y(°) Delta_x(°) Delta_y(°) Delta_z Celda_x Celda_y Celda_z LatMedia
{0} {0} {0} {0} {0} {0} {0} {0} {0}
*-------------------------------------------------------------------------------------
* MALLA DE PROBABILIDADES o CONCENTRACIONES: (SI GRABA_CONC=1)
*--------------------------------------------------------------------------------------
* Nombre_malla
{filename_parameters["grid_filename"]}
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
{1}
*--------------------------------------------------
* VERTIDO:
*--------------------------------------------------
* TIPO_DE_VERTIDO_FLOTANTE(1)_FUEL(2)_HNS(3)
{substance_type}
* SIMULO_SPREADING(0:NO;1:SI) ALGORTIMO_SPREADING((1=ALG_DIF.EQUIVALENTE[ADIOS2],2=ALG_ELIPSOIDAL[LEHR],3=ALG_RABEH-KOLLURU[MOHID-HNS])) TIEMPO_PARADA_SPREADING_CUANDO_FUEL (horas)
{1 if simulation_parameters["spreading"] else 0}    {spreading_formulation}    {simulation_parameters["spreading_duration"].total_seconds()/3600}
* SIMULO_EVAPORACION(0:NO;1:SI)****SOLO_SI_TIPO_DE_VERTIDO=2 y 3
{1 if simulation_parameters["evaporation"] else 0}
* SIMULO_EMULSIONADO(0:NO;1:SI)****SOLO_SI_TIPO_DE_VERTIDO=2
{1 if simulation_parameters["emulsification"] else 0}
* SIMULO DISPERSIÓN VERTICAL (ENTRAINMENT) = 0:NO; 1:SÍ ****SOLO_SI_TIPO_DE_VERTIDO=2 y 3
{1 if simulation_parameters["vertical_dispersion"] else 0}
* SIMULO_DISOLUCION VOLATILIZACION SEDIMENTACION BIODEGRADACION_LARGOPLAZO (0:NO;1:SI)****SOLO_SI_TIPO_DE_VERTIDO=3
{1 if simulation_parameters["dissolution"] else 0}   {1 if simulation_parameters["volatilization"] else 0}   {1 if simulation_parameters["sedimentation"] else 0}    {1 if simulation_parameters["biodegradation"] else 0}
* VISC_CINEMATICA_AGUA_MAR(m2/s)
{simulation_parameters["seawater_kinematic_viscosity"]}
* Datos de vertidos:
* VERTIDO INSTANTANEO(1) O CONTINUO-3D(2)
{release_type}
* SI VERTIDO INSTANTANEO: Nº_PUNTOS_DE_VERTIDO
{len(simulation_parameters["spill_points"])}
* SI VERTIDO CONTINUO-3D: DURACION VERTIDO (horas) DT_PULSOS(segundos - Indicaciones: número divisible de la duración del vertido y mayor y múltiplo del paso de tiempo de cálculo --> Si es mayor que DT_PARTS definido en .run, se toma DT_PARTS-es valor máximo para que no haya saltos en graficado))
* A tener en cuenta: cuanto menor es el DT_PULSOS, mayor será el tiempo de cómputo ya que se introducen más partículas en el medio
{simulation_parameters["release_duration"].total_seconds()/3600}   {simulation_parameters["release_timestep"].total_seconds()}
* PROPIEDADES VERTIDO/MEDIO
* ID T_inicio Masa   Coord_x  Coord_y   z   Ancho_x Ancho_y Espesor EspMin Volum_TOT    TIPO_FUEL       DENS  TEMP_D0 VISC_K TEMP_V0 WATER_SOLUBILITY  TEMP_SOL  VAPOUR_PRESS TEMP_VP  MOL_WEIGHT  ORGANIC EVAP_MAX EVAP_MIN EMULS_MAX  DENSIDAD_MAR  TEMP_MAR TEMP_AIR
*      (h)    (Kg)     (°)      (°)  (si 3D)(en sup)(en sup)  (OIL)    (m)   M/D(m3)      (OIL)        (kg/m3) (ºC)   (cSt)   (ºC)       (SI NHS)        (ºC)      (SI NHS)     (ºC)    (kg/kmol) (SI NHS)   (%)      (%)     (OIL)       (kg/m3)      (ºC)    (ºC)
*      (h)    (Kg)     (°)     (°)    (m)    (m)     (m)      (m)     (m)   M/D(m3) CRUDO=0/REFINADO=1 (kg/m3) (ºC)   (cSt)   (ºC)   (mg/L)(max10E7)    (ºC)       (KPa)       (ºC)    (kg/kmol)   1:SI     (%)      (%)      (%)        (kg/m3)      (ºC)    (ºC)
{table1}
* PROPIEDADES EXTRA VERTIDO/MEDIO SI TIPO_DE_VERTIDO es 3 (HNS)  [TANTAS LINEAS COMO PUNTOS DE VERTIDO]
* ID  ConcentracionSS  Sorption_coef(LogKoc)  Degrad_rate
*	    (Si HNS)			(Si HNS)		   (Si HNS)
*	     (mg/L)				 (-)  			   (day-1)
{table2}
*--------------------------------------------------
* SIMULACION NUMERICA:
*--------------------------------------------------
* TIEMPO_TOTAL(h)
{simulation_parameters["duration"].total_seconds()/3600}
*
* FORZAMIENTOS:
*--------------------------------------------------
***
* CORRIENTES:
* CORRIENTES_POR_FICHERO(1)_O_FIJO(2) Tipo_Malla(1=regular,0=irregular) Tipo_Dato(0=MallaConstante,1=MallaVariable) ModoVariable(1=MojoSeco,2=Radar)
* MODIFICACION_CORRIENTES_POR_PARÁMETROS_EXTERNOS(0:NO;1:SI)!_SIEMPRE_QUE_CORRIENTES_SEAN_POR_FICHERO Us_Vs_(Ws)_mismo_file(0=No,1=Sí)
{2 if forcing_parameters["currents_n_points"] == 1 else 1} {1} {0} {1} {0} {1}
* SI_VERTIDO_3D_CORRIENTES_COLUMNA_POR_CAPAS(1)_O_PROMEDIADAS_EN_VERTICAL-zonaXYVertido(2)****OPCIÓN PROMEDIADAS_EN_VERTICAL(2) de momento SOLO_SI_CORRIENTES_POR_FICHERO, Tipo_Malla_Regular, Tipo_Dato_MallaConstante, Us_Vs_mismo_file(sin Ws), interpolaciones 0
{2}
* FORMATO MALLA  FORMATO MALLA_PARCORRECTOR [(1:xyz; 2:grid)] [NOTA:GRID PARA CORRIENTES EN MALLA REGULAR Y DATOS POR FICHERO]
{1} {2}
* TIEMPO_ENTRE_FICHEROS(h) Nº_DE_FICHEROS_O_DE_LINEAS_DE_LA_TABLA  Nº_DE_FICHEROS_CORRECTORES(=_Nº_FICHEROS_CORRIENTES)
{forcing_parameters["currents_dt"]}   {forcing_parameters["currents_nt"]}    {forcing_parameters["currents_nt"]}
* SI_FORMATO_MALLA=1 O FORMATO_MALLACORRECTOR=1::Nº_NODOS_U  Nº_NODOS_V  Nº_NODOS_W
{forcing_parameters["currents_n_points"]}    {forcing_parameters["currents_n_points"]}    {forcing_parameters["currents_n_points"]}
* SI_FORMATO_MALLA=2 O FORMATO_MALLACORRECTOR=2 LEER::
* COMPONENTE_U: ORIGEN_X(°) ORIGEN_Y(°) DELTA_X(°) DELTA_Y(°) CELDA_X CELDA_Y
{0} {0} {0} {0} {0} {0}
* COMPONENTE_V: ORIGEN_X(°) ORIGEN_Y(°) DELTA_X(°) DELTA_Y(°) CELDA_X CELDA_Y
{0} {0} {0} {0} {0} {0}
***
* OLEAJE:
* OLEAJE_POR_FICHERO(1)_O_FIJO(2-m,º,s)  Tipo_Malla(1=regular,0=irregular)
{2 if forcing_parameters["waves_n_points"] == 1 else 1}  {1}
* FORMATO MALLA(1:xyz; 2:grid)
{1}
* TIEMPO_ENTRE_FICHEROS(h); Nº_DE_FICHEROS_O_DE_LINEAS_DE_LA_TABLA
{forcing_parameters["waves_dt"]}   {forcing_parameters["waves_nt"]}
* SI_FORMATO_MALLA=1:: Nº_DE_PUNTOS (HS_T_y_Dir_en_el_mismo_fichero)
{forcing_parameters["waves_n_points"]}
* SI_FORMATO_MALLA=2:: ORIGEN_X(°) ORIGEN_Y(°) DELTA_X(°) DELTA_Y(°) CELDA_X CELDA_Y [Variables_en_ficheros_individuales]
{0} {0} {0} {0} {0} {0}
***
* VIENTO:
* VIENTO_POR_FICHERO(1)_O_FIJO(2-m/s,º) Tipo_Malla(1=regular,0=irregular)
{2 if forcing_parameters["winds_n_points"] == 1 else 1}  {1}
* FORMATO MALLA(1:xyz; 2:grid)
{1}
* TIEMPO_ENTRE_FICHEROS(h) Nº_DE_FICHEROS_O_DE_LINEAS_DE_LA_TABLA
{forcing_parameters["winds_dt"]}   {forcing_parameters["winds_nt"]}
* SI_FORMATO_MALLA=1:: Nº_DE_PUNTOS (Uw_y_Vw_en_el_mismo_fichero)
{forcing_parameters["winds_n_points"]}
* SI_FORMATO_MALLA=2:: ORIGEN_X(°) ORIGEN_Y(°) DELTA_X(°) DELTA_Y(°) CELDA_X CELDA_Y [Variables_en_ficheros_individuales]
{0} {0} {0} {0} {0} {0}
* FACTORES (4 PRIMERAS COLUMNAS) | DIFUSION (3 RESTANTES) [TANTAS LINEAS COMO PUNTOS DE VERTIDO]
*--------------------------------------------------
* FACTOR_CURRENTS CD_VIENTO(0.03-0.05):ALFA	 CD_VIENTO:BETA  FACTOR_OLEAJE  DISPERSION(0:NO,1:SI)  D   KZ(m2/s)[0.01 sobre 30 m:DeDominicis2013]_(K1,2=D;K3=KZ->SIEMPRE QUE MEDIO_EJECUCION=1) S(Pdte_supf_agua-> SIEMPRE QUE MEDIO_EJECUCION=2)
{table3}
*--------------------------------------------------
* DIRECTORIO DATOS:
*------------------------------------------------------
* SI DIRECTORIO_DATOS_EJECUCION_MODELO=2 -> AÑADIR NUEVA RUTA(); SI DIRECTORIO=1->AÑADIR la ruta no cambia
{filename_parameters["inputs_directory"]}
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cfg_txt)
    return output_path


def create_tables(
    spill_points: list[dict],
    substance_type: str,
    seawater_temperature: float,
    seawater_density: float,
    air_temperature: float,
    suspended_solid_concentration: float,
) -> tuple[str, str, str]:
    """create tables to define spill point related data in cfg-file

    Args:
        spill_points (list[dict]): spill point definitions
        substance_type (str): type of the susbtances
        seawater_temperature (float): value for seawater temperature (º)
        seawater_density (float): value for seawater density (º)
        air_temperature (float): value for air temperature (º)
        suspended_solid_concentration (float): value for suspended solid concentration (kg/m3)

    Returns:
        tuple[str, str, str]: tables required in cfg-file
    """
    df_spill_points = create_spill_points_df(spill_points)
    df_substances = create_substances_df(
        [d["substance"] for d in spill_points if "substance" in d.keys()],
        substance_type,
    )
    df_climate_vars = create_climate_df(
        len(spill_points),
        seawater_temperature,
        seawater_density,
        air_temperature,
        suspended_solid_concentration,
    )
    data = pd.concat([df_spill_points, df_substances, df_climate_vars], axis=1)

    df = pd.DataFrame(
        [], columns=CFG_KEYS_FOR_TABLE_1 + CFG_KEYS_FOR_TABLE_2 + CFG_KEYS_FOR_TABLE_3
    )
    df = pd.concat([df, data]).fillna(0)

    # Calculate volume
    df["volume"] = (df["mass"] / df["density"]).fillna(0)
    # Convert boolean to [0,1]
    df["organic"] = df["organic"].astype(int).fillna(0)
    # Convert to [0,1]
    df["oil_type"].loc[df["oil_type"] == "refined"] = 1
    df["oil_type"].loc[df["oil_type"] == "crude"] = 0
    # ID starting in 1
    df.index += 1

    df = df.fillna(0)
    df1 = df.get(CFG_KEYS_FOR_TABLE_1)
    df2 = df.get(CFG_KEYS_FOR_TABLE_2)
    df3 = df.get(CFG_KEYS_FOR_TABLE_3)

    return (
        df1.to_string(header=False),
        df2.to_string(header=False),
        df3.to_string(header=False, index=False),
    )


def create_spill_points_df(spill_points: list[dict]) -> pd.DataFrame:
    dfs = []
    for d in spill_points:
        dfs.append(pd.DataFrame([d]))
    df = pd.concat(dfs).reset_index(drop=True)
    df.index += 1
    return df


def create_substances_df(
    substance_names, substance_type, source="local"
) -> pd.DataFrame:
    if not substance_names:
        return pd.DataFrame([])
    else:
        substances = {}
        for substance_name in list(set(substance_names)):
            if source.lower() == "local":
                substances[substance_name] = pd.DataFrame(
                    [import_local(substance_type, substance_name)]
                )
            else:
                raise NotImplementedError(
                    "Call to external API and return substance dict {substance_name: dataframe}"
                )
        dfs = [substances[substance_name] for substance_name in substance_names]
        df = pd.concat(dfs).reset_index()
        df.index += 1
        return df


def create_climate_df(
    n_spill_points,
    seawater_temperature,
    seawater_density,
    air_temperature,
    suspended_solid_concentration,
):
    df = pd.DataFrame(
        {
            "seawater_temperature": [seawater_temperature] * n_spill_points,
            "seawater_density": [seawater_density] * n_spill_points,
            "air_temperature": [air_temperature] * n_spill_points,
            "suspended_solid_concentration": [suspended_solid_concentration]
            * n_spill_points,
        }
    )
    df.index += 1
    return df


def translate_spreading_formulation(keyword):
    if keyword.lower() == "adios2":
        return 1
    elif keyword.lower() == "lehr":
        return 2
    elif keyword.lower() == "mohid-hns":
        return 3
    else:
        raise ValueError("Invalid spreading formulation")


def translate_release_type(keyword):
    if keyword.lower() == "instantaneous":
        return 1
    elif keyword.lower() == "continuous":
        return 2
    else:
        raise ValueError("Invalid release type")


def translate_substance_type(keyword):
    if keyword.lower() == "drifter":
        return 1
    elif keyword.lower() == "oil":
        return 2
    elif keyword.lower() == "hns":
        return 3
    else:
        raise ValueError("invalid particle type")
