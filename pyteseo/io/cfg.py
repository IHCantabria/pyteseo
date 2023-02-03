from datetime import datetime, timedelta
import pandas as pd


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


def set_time(
    initial_datetime: datetime, duration: timedelta, timestep: timedelta
) -> dict:
    """set simulation time options

    Args:
        initial_datetime (datetime): datetime of the simulation initiation
        duration (timedelta): duration of the simulation
        timestep (timedelta): timestep of the simulation

    Returns:
        dict: time configurations
    """
    return {
        "initial_datetime": initial_datetime.isoformat(),
        "duration": duration.total_seconds() / 3600,
        "timestep": timestep.total_seconds(),
    }


def set_climate_vars(
    air_temp: float = 14,
    sea_temp: float = 20,
    sea_dens: float = 1025,
    sea_c_visc: float = 1.004e-6,
):
    """set simulation climate variables

    Args:
        air_temp (float, optional): air temperature, (ºC). Defaults to 14.
        sea_temp (float, optional): seawater surface temperature, (ºC). Defaults to 20.
        sea_dens (float, optional): seawater density, (kg/m3). Defaults to 1025.
        sea_c_visc (float, optional): seawater cinematic viscosity, (m2/s). Defaults to 1.004e-6.

    Returns:
        _type_: _description_
    """
    return {
        "air_temperature": air_temp,
        "seawater_temperature": sea_temp,
        "seawater_density": sea_dens,
        "seawater_cinematic_viscosity": sea_c_visc,
    }


# instantaneous
def set_instantaneous_release(n_points: int) -> dict:
    """set instantaneous release configuration

    Args:
        n_points (int): number of spill points

    Returns:
        dict: release configuration
    """
    return {"type": "instantaneous", "parameters": {"n_points": n_points}}


# continuous
def set_continuous_release(
    n_points: int, release_duration: timedelta, subspill_timestep: timedelta
) -> dict:
    """set continuous release configuration

    Args:
        n_points (int): number of spill points
        release_duration (timedelta): duration of the release
        subspill_timestep (timedelta): timestep between subspills

    Returns:
        dict: release onfiguration
    """
    return {
        "type": "continuous",
        "parameters": {
            "n_points": n_points,
            "release_duration": release_duration.total_seconds() / 3600,
            "subspill_timestep": subspill_timestep.total_seconds(),
        },
    }


def set_simulation_parameters(
    simulation_type: str = "2d",
    motion_type: str = "forwards",
    weathering_type: str = "drifter",
) -> dict:
    """set simulation parameters

    Args:
        simulation_type (str): "2d", "quasi3d", "3d". Defaults to "2d".
        weathering_type (str): "drifter", "oil", "hns". Defaults to "drifter".
        motion (str, optional): "forwards" or "backwards". Defaults to "forwards".

    Returns:
        dict: simulation parameters
    """
    simulation_types = ["2d", "quasi3d", "3d"]
    weathering_types = ["drifter", "oil", "hns"]
    motion_types = ["forwards", "backwards"]

    if simulation_type.lower() not in simulation_types:
        raise ValueError(
            f"Invalid keyword ({simulation_type.lower()}), use one of these {simulation_types}"
        )

    if weathering_type.lower() not in weathering_types:
        raise ValueError(
            f"Invalid keyword ({weathering_type.lower()}), use one of these {weathering_types}"
        )

    if motion_type.lower() not in motion_types:
        raise ValueError(
            f"Invalid keyword ({motion_type.lower()}), use one of these {motion_types}"
        )

    return {
        "simulation_type": simulation_type,
        "motion_type": motion_type,
        "weathering_type": weathering_type,
    }


def set_spreading_config(spreading_type: str, duration: timedelta) -> dict:
    """set spreading configuration

    Args:
        spreading_type (str): "adios2", "lehr", "mohid-hns". (ref: TODO - papers)
        duration (timedelta): spreading duration for "adios2" and "lehr".

    Returns:
        dict: spreading configuration
    """
    valid_keywords = ["adios2", "lehr", "mohid-hns"]
    if spreading_type.lower() not in valid_keywords:
        raise ValueError(
            f"Invalid keyword ({spreading_type.lower()}), use one of these {valid_keywords}"
        )
    return {
        "spreading_type": spreading_type,
        "spreading_duration": duration.total_seconds() / 3600,
    }


def set_processes(
    spreading: bool,
    evaporation: bool,
    emulsification: bool,
    vertical_dispersion: bool,
    disolution: bool,
    volatilization: bool,
    sedimentation: bool,
    biodegradation: bool,
) -> dict:
    """set flags to activate or not each process

    Args:
        spreading (bool): activate spreading (oil/hns)
        evaporation (bool): activate evaporation (oil/hns)
        emulsification (bool): activate emulsion (oil)
        vertical_dispersion (bool): activate vertical dispersion (oil/hns)
        disolution (bool): activate disolution (hns)
        volatilization (bool): activate volatilization (hns)
        sedimentation (bool): activate sedimentation (hns)
        biodegradation (bool): activate biodegradation (hns)

    Returns:
        dict: flags for activate processes
    """
    return {
        "spreading": spreading,
        "evaporation": evaporation,
        "emulsification": emulsification,
        "vertical_dispersion": vertical_dispersion,
        "disolution": disolution,
        "volatilization": volatilization,
        "sedimentation": sedimentation,
        "biodegradation": biodegradation,
    }


def set_hns_table(
    n_spill_points: int,
    suspended_solids: list[float] = [10],
    sorption_coeficient: list[float] = [-0.32],
    degradation_rate: list[float] = [0],
) -> str:
    """set hns table

    Args:
        n_spill_points (int): number of spill points
        suspended_solids (list[float], optional): concentration of suspended solids, [mg/L]. Defaults to [10].
        sorption_coeficient (list[float], optional): sorption coeficient of the sustance, [-]. Defaults to [-0.32].
        degradation_rate (list[float], optional): degradation rate, [day-1]. Defaults to [0].

    Returns:
        str: hns table
    """
    suspended_solids = (
        [suspended_solids]
        if not isinstance(suspended_solids, list)
        else suspended_solids
    )
    sorption_coeficient = (
        [sorption_coeficient]
        if not isinstance(sorption_coeficient, list)
        else sorption_coeficient
    )
    degradation_rate = (
        [degradation_rate]
        if not isinstance(degradation_rate, list)
        else degradation_rate
    )

    suspended_solids = (
        suspended_solids * n_spill_points
        if len(suspended_solids) == 1
        else suspended_solids
    )
    sorption_coeficient = (
        sorption_coeficient * n_spill_points
        if len(sorption_coeficient) == 1
        else sorption_coeficient
    )
    degradation_rate = (
        degradation_rate * n_spill_points
        if len(degradation_rate) == 1
        else degradation_rate
    )

    df = pd.DataFrame(
        {
            "suspended_solids": suspended_solids,
            "sorption_coeficient": sorption_coeficient,
            "degradation_rate": degradation_rate,
        }
    )
    df.index = df.index + 1
    return df.to_string(header=False)


def set_spill_points_cfg(
    n_spill_points: int,
    release_time: list[timedelta],
    lon: list[float],
    lat: list[float],
    depth: list[float] = [0],
    width: list[float] = [1],
    length: list[float] = [1],
    mass: list[float] = [0],
    volume: list[float] = [0],
    thickness: list[float] = [0],
) -> pd.DataFrame:
    """create intermediate DataFrame with general spill point cfg

    Args:
        release_time (list[timedelta]): increment of time to initiate the release relative to the initiation of the simulation
        lon (list[float]): X-coordinate of the spill point, (º).
        lat (list[float]): Y-coordinate of the spill point, (º).
        depth (list[float], optional): Z-coordinate of the spill point, (m). Defaults to 0.
        width (list[float], optional): width of the spill in X-axis, (m). Defaults to 1.
        length (list[float], optional): length of the spill in Y-axis, (m). Defaults to 1.
        mass (list[float], optional): total mass spilled, (kg). Defaults to 0.
        volume (list[float], optional): total volume spilled, (m3). Defaults to 0.
        thickness (list[float], optional): thickness of the initial spill, (m). Defaults to 0.

    Returns:
        pd.DataFrame: spill point configuration
    """
    release_time = (
        [release_time] if not isinstance(release_time, list) else release_time
    )
    lon = [lon] if not isinstance(lon, list) else lon
    lat = [lat] if not isinstance(lat, list) else lat
    depth = [depth] if not isinstance(depth, list) else depth
    width = [width] if not isinstance(width, list) else width
    length = [length] if not isinstance(length, list) else length
    mass = [mass] if not isinstance(mass, list) else mass
    volume = [volume] if not isinstance(volume, list) else volume
    thickness = [thickness] if not isinstance(thickness, list) else thickness

    release_time = (
        release_time * n_spill_points if len(release_time) == 1 else release_time
    )
    lon = lon * n_spill_points if len(lon) == 1 else lon
    lat = lat * n_spill_points if len(lat) == 1 else lat
    depth = depth * n_spill_points if len(depth) == 1 else depth
    width = width * n_spill_points if len(width) == 1 else width
    length = length * n_spill_points if len(length) == 1 else length
    mass = mass * n_spill_points if len(mass) == 1 else mass
    volume = volume * n_spill_points if len(volume) == 1 else volume
    thickness = thickness * n_spill_points if len(thickness) == 1 else thickness

    df = pd.DataFrame(
        {
            "release_time": [dt.total_seconds() / 3600 for dt in release_time],
            "lon": lon,
            "lat": lat,
            "depth": depth,
            "widht": width,
            "lenght": length,
            "thickness": thickness,
            "mass": mass,
            "volume": volume,
        }
    )
    if len(df) != n_spill_points:
        raise ValueError(
            f"The number of spill points ({n_spill_points}) is not equal to the number of inputs provided"
        )
    return df


def set_substance_cfg() -> pd.DataFrame:
    pass


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
