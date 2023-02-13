from pyteseo.defaults import RUN_MAIN_PARAMETERS
from pyteseo.io.utils import _add_default_parameters


def generate_parameters_for_run(user_parameters) -> dict:
    return _add_default_parameters(user_parameters, RUN_MAIN_PARAMETERS)


def write_run(path, run_parameters, first_time_saved, n_coastal_polygons):

    environment = _translate_environment(run_parameters["environment"])
    mode = _translate_mode(run_parameters["mode"])
    motion = _translate_motion(run_parameters["motion"])
    beaching_algorithm = _translate_beaching_algorithm(
        run_parameters["beaching_algorithm"]
    )
    execution_scheme = _translate_execution_scheme(run_parameters["execution_scheme"])

    run_txt = f"""*--------------------------------------------------
* FICHERO RUN PARA TTEREG.F90
*--------------------------------------------------
*
* MEDIO_EJECUCION_MARINO(1)_RIOS(2)
{environment}
* SIMULACIÓN 2D(1) O 3D(2)
{mode}
* CUANDO SIMULACIÓN 3D: TIPO BLOWOUT (incluye lectura resultados campo cercano): SI(1)_NO(0)
{int(run_parameters["near_field_3d"])}
* DIRECCION_PREDICCION_FORWARD(1)_BACKWARD(2)
{motion}
* DIRECTORIO_DATOS_EJECUCIONMODELO(1:DIRECTORIO_ACTUAL(MISMO_SITIO_EJECUTABLE), 2:OTRO_DIRECTORIO)
{int(run_parameters["input_directory"])+1}
****************************************************************************************
* BUSQUEDA_TIERRA(:1)_COSTA(:2)_(1=SoloMascaraModelo,2=InteraccionMascaraModeloCosta)
{int(run_parameters["use_coastline"])+1}
* ALGORITMO_BUSQUEDA_COSTA(1=LowResolution[Regional],2=HighResolution[Local])
{beaching_algorithm}
* NUMERO_DE_POLIGONOS_QUE_DEFINEN_LA_COSTA(UNICAMENTE_PARA_HighResolution)
{n_coastal_polygons}
****************************************************************************************
* NUMERO_DE_PARTICULAS/VERTIDO (3D, mínimo 5 por 5 clases de tamaño de particula)  LECTURA DE POSICIONES=RESTART (0=NO, 1=SI)(De momento solo valido si tipo vertido Flotante-Plasticos)
{run_parameters["n_particles"]}  {int(run_parameters["use_restart"])}
* INCREMENTO_DE_t(s)
{run_parameters["timestep"].total_seconds()}
* INTERPOLACIÓN TEMPORAL(1:SI,0:NO)_VIENTO _OLEAJE _CORRIENTES
{int(run_parameters["use_time_interpolation_winds"])} {int(run_parameters["use_time_interpolation_waves"])} {int(run_parameters["use_time_interpolation_currents"])}
* ESQUEMA_EULER(1)_RUNGE-KUTTA(2)
{execution_scheme}
*
*--------------------------------------------------
* RESULTADOS | DERIVADOS[[1]] BORRAR_FICHEROS_FORZAMIENTO[[0]]
*--------------------------------------------------
* TIEMPO_PRIMERA_ESCRIT(h) DT_PARTS(s) DT_MALLA(s) DT_PROPRIEDADES(s)
{(run_parameters["forcing_init_datetime"] - first_time_saved).total_seconds()}  {run_parameters["particles_save_dt"].total_seconds()}   {run_parameters["grids_save_dt"].total_seconds()} {run_parameters["properties_save_dt"].total_seconds()}
* GRABAR_RESULTADOS(1:SI,0:NO) _PARTICULAS _MALLA _PROPIEDADES
{int(run_parameters["save_particles"])}  {int(run_parameters["save_grids"])}   {int(run_parameters["save_properties"])}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(run_txt)


def _translate_environment(keyword):
    if keyword.lower() == "marine":
        return 1
    elif keyword.lower() == "riverine":
        return 2
    else:
        raise TypeError(f"invalid parameter in run-file (environment = {keyword})")


def _translate_mode(keyword):
    if keyword.lower() == "2d":
        return 1
    elif keyword.lower() == "3d":
        return 2
    else:
        raise TypeError(f"invalid parameter in run-file (mode = {keyword})")


def _translate_motion(keyword):
    if keyword.lower() in ["forward", "forwards"]:
        return 1
    elif keyword.lower() in ["backward", "backwards", "backtracking"]:
        return 2
    else:
        raise TypeError(f"invalid parameter in run-file (motion = {keyword})")


def _translate_beaching_algorithm(keyword):
    if keyword.lower() in ["regional", "low"]:
        return 1
    elif keyword.lower() in ["local", "high"]:
        return 2
    else:
        raise TypeError(
            f"invalid parameter in run-file (beaching_algorithm = {keyword})"
        )


def _translate_execution_scheme(keyword):
    if keyword.lower() == "euler":
        return 1
    elif keyword.lower() == "runge-kutta":
        return 2
    else:
        raise TypeError(f"invalid parameter in run-file (execution_scheme = {keyword})")
