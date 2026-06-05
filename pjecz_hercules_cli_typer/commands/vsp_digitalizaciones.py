"""
VASPEC Digitalizaciones command
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Annotated

import pytz
from openpyxl import Workbook
from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Option, Typer

from pjecz_hercules_cli_typer.config.settings import get_settings
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.vsp_digitalizaciones import VspDigitalizacion
from pjecz_hercules_cli_typer.utils.database import get_database
from pjecz_hercules_cli_typer.utils.google_cloud_storage import (
    FileNotFoundError,
    get_blob_from_gcs,
    update_blob_name_in_gcs,
)
from pjecz_hercules_cli_typer.utils.safe_string import safe_clave, safe_string

bitacora = logging.getLogger(__name__)
bitacora.setLevel(logging.INFO)
formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
empunadura = logging.FileHandler("logs/vsp-digitalizaciones.log")
empunadura.setFormatter(formato)
bitacora.addHandler(empunadura)

app = Typer(help="VASPEC Digitalizaciones")


@app.command()
def actualizar(
    autoridad_clave: str = "",
    save: Annotated[bool, Option("--save", "-s", help="Guardar cambios en la base de datos")] = False,
):
    """Actualizar las digitalizaciones para renombrar la URL pública a UUID, definir tamaño y tiempo de subida en GCS"""
    console = Console()
    if save:
        console.print("Actualizando las digitalizaciones en el bucket final...")
        title = "Se han actualizado las siguientes digitalizaciones:"
    else:
        console.print("Mostrando las digitalizaciones que se pueden actualizar...")
        title = "Estas digitalizaciones se podrían actualizar:"

    # Obtener configuración
    config = get_settings()

    # Validar que se haya configurado el depósito
    if config.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES == "":
        console.print("[red]No se ha configurado el depósito[/red]")
        raise Exit(code=1)

    # Inicializar los contadores de archivos encontrados y copiados
    contador_actualizados = 0
    contador_no_encontrados = 0
    contador_sin_cambios = 0

    # Inicializar la base de datos
    db = get_database()

    # Si viene la autoridad_clave, consultarla
    autoridades = []
    if autoridad_clave != "":
        autoridad = db.query(Autoridad).filter(Autoridad.clave == safe_clave(autoridad_clave)).first()
        if autoridad is None:
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)
        autoridades.append(autoridad)
    else:
        # De lo contrario, consultar las autoridades donde es_vsp_digitalizaciones es True
        autoridades = db.query(Autoridad).filter(Autoridad.es_vsp_digitalizaciones).order_by(Autoridad.clave).all()
        if autoridades is None:
            console.print("[yellow]No se encontraron autoridades con digitalizaciones[/yellow]")
            return

    # Inicializar la tabla
    tabla = Table(title=title)
    tabla.add_column("Autoridad clave")
    tabla.add_column("Expediente")
    tabla.add_column("Descripción")
    tabla.add_column("Tamaño (bytes)")
    tabla.add_column("Archivo anterior (blob name)")
    tabla.add_column("Archivo nuevo (blob name)")

    # Bucle por cada autoridad
    for autoridad in autoridades:
        # Consultar las digitalizaciones de esa autoridad
        digitalizaciones = (
            db.query(VspDigitalizacion)
            .join(Autoridad)
            .filter(
                Autoridad.id == autoridad.id,
                VspDigitalizacion.estatus == "A",
            )
            .all()
        )

        # Bucle por cada digitalización
        for digitalizacion in digitalizaciones:
            # Si el archivo tiene UUID en el nombre
            es_uuid = False
            try:
                parts = digitalizacion.archivo.split("/")
                archivo_part = parts[-1]  # Obtener la parte del nombre del archivo
                archivo_nombre = archivo_part.split(".")[0]  # Obtener la parte del nombre sin la extensión
                if len(archivo_nombre) == 36:  # Longitud de un UUID
                    es_uuid = True
            except (IndexError, ValueError) as error:
                console.print(f"[yellow]Error al separar las partes:[/yellow] {digitalizacion.archivo} {error}")
                contador_no_encontrados += 1
                continue

            # Obtener el blob de la digitalización
            try:
                blob = get_blob_from_gcs(config.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES, digitalizacion.archivo)
            except FileNotFoundError:
                console.print(f"[yellow]No se encuentra este archivo:[/yellow] {digitalizacion.archivo}")
                contador_no_encontrados += 1
                continue
            except Exception as error:
                console.print(f"[red]Error al obtener este archivo:[/red] {digitalizacion.archivo} {error}")
                raise Exit(code=1)

            # Tomar el nombre original, y validar que el blob tenga un nombre, si no, se omite
            original_blob_name = blob.name
            if original_blob_name is None:
                console.print(f"[yellow]Archivo sin nombre: {blob}[/yellow]")
                contador_no_encontrados += 1
                continue

            # Por defecto, se asume que no hay cambios
            hay_cambios = False

            # Si es_uuid es falso, vamos a renombrar el archivo en el bucket
            if not es_uuid:
                # Definir el nuevo nombre
                nuevo_blob_name = f"{autoridad.clave}/{digitalizacion.expediente_anio}/{str(digitalizacion.archivo_uuid)}.pdf"
                # Renombrar archivo en el bucket
                if save:
                    try:
                        digitalizacion.url = update_blob_name_in_gcs(
                            config.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES,
                            original_blob_name,
                            nuevo_blob_name,
                        )
                    except Exception as error:
                        console.print(f"[red]Error al renombrar el archivo {original_blob_name}: {error}[/red]")
                        raise Exit(code=1)
                # Cambiar el nombre del archivo en la base de datos
                digitalizacion.archivo = nuevo_blob_name
                # Hay cambios
                hay_cambios = True

            # Si NO tiene tamaño o si es diferente al tamaño del blob, se actualiza
            if not digitalizacion.tamano or digitalizacion.tamano != blob.size:
                digitalizacion.tamano = blob.size if blob.size else None
                hay_cambios = True

            # Si NO tiene tiempo o si es diferente al tiempo de actualización del blob, se actualiza
            if not digitalizacion.tiempo or digitalizacion.tiempo != blob.updated:
                digitalizacion.tiempo = blob.updated if blob.updated else None
                hay_cambios = True

            # Si hay cambios, se actualiza la base de datos
            if hay_cambios:
                if save:
                    db.add(digitalizacion)
                    db.commit()
                contador_actualizados += 1
            else:
                contador_sin_cambios += 1

            # Agregar el reglón a la tabla
            tabla.add_row(
                autoridad.clave,
                digitalizacion.expediente,
                digitalizacion.descripcion,
                str(digitalizacion.tamano) if digitalizacion.tamano else "N/A",
                original_blob_name,
                digitalizacion.archivo,
            )

    # Mostrar tabla
    if contador_actualizados:
        console.print(tabla)

    if save:
        if contador_actualizados:
            console.print(f"[bold green]Se actualizaron {contador_actualizados} en la base de datos.[/bold green]")
    else:
        if contador_actualizados:
            console.print(f"[bold green]Se podrían actualizar {contador_actualizados}.[/bold green]")
    if contador_sin_cambios:
        console.print(f"[cyan]Hay {contador_sin_cambios} que no necesitan cambios.[/cyan]")
    if contador_no_encontrados:
        console.print(f"[red]LAMENTABLEMENTE hay {contador_no_encontrados} SIN archivo.[/red]")


@app.command()
def copiar(
    autoridad_clave: str = "",
    save: Annotated[bool, Option("--save", "-s", help="Guardar cambios en la base de datos")] = False,
):
    """Copiar las nuevas digitalizaciones del bucket original al bucket final con rclone"""
    console = Console()
    if save:
        console.print("Ejecutando los comandos para revisar y copiar entre buckets...")
        title = "Se copiaron estos nuevos archivos al bucket de destino:"
    else:
        console.print("Mostrando los comandos para revisar y copiar entre buckets...")
        title = "Estos archivos se podrían copiar al bucket de destino:"

    # Inicializar los contadores de archivos encontrados y copiados
    contador_encontrados = 0
    contador_copiados = 0

    # Obtener configuración
    config = get_settings()

    # Inicializar la base de datos
    db = get_database()

    # Si viene la autoridad_clave, consultarla
    autoridades = []
    if autoridad_clave != "":
        autoridad = db.query(Autoridad).filter(Autoridad.clave == safe_clave(autoridad_clave)).first()
        if autoridad is None:
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)
        autoridades.append(autoridad)
    else:
        # De lo contrario, consultar las autoridades donde es_vsp_digitalizaciones es True
        autoridades = db.query(Autoridad).filter(Autoridad.es_vsp_digitalizaciones).order_by(Autoridad.clave).all()
        if autoridades is None:
            console.print("[yellow]No se encontraron autoridades con digitalizaciones[/yellow]")
            return

    # Inicializar la tabla
    tabla = Table(title=title)
    tabla.add_column("Autoridad clave")
    tabla.add_column("Expediente")
    tabla.add_column("Descripción")
    tabla.add_column("Tamaño (bytes)")
    tabla.add_column("Archivo (blob name)")

    # Bucle por cada autoridad
    for autoridad in autoridades:
        # Definir el directorio en el bucket de origen
        origen_dir = autoridad.clave.lower()
        if config.VASPEC_DIR != "":
            origen_dir = f"{config.VASPEC_DIR}/{origen_dir}"

        # Definir la ruta en el bucket de origen
        remoto_origen = f"{config.RCLONE_REMOTE_ORIGEN}:/{config.CLOUD_STORAGE_DEPOSITO_VASPEC}/{origen_dir}"
        console.print(f"Obteniendo años en [cyan]{remoto_origen}[/cyan]...")

        # Obtener el listado de directorios de años en el bucket de origen
        result = subprocess.run(["rclone", "lsjson", remoto_origen], capture_output=True, text=True, check=True)
        if result.returncode != 0:
            console.print(f"[red]Error en rclone:[/red] {result.returncode}")
            raise Exit(code=result.returncode)
        try:
            anios = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            console.print(f"[red]Error al decodificar JSON:[/red] {error}")
            raise Exit(code=1)

        # Bucle por cada año encontrado
        for anio in anios:
            if anio.get("IsDir") is not True:
                continue  # Si NO es un directorio, se omite

            # Si el nombre del directorio no es un número de cuatro dígitos, se omite
            if not anio.get("Name", "").isdigit() or len(anio.get("Name", "")) != 4:
                console.print(f"[yellow]Se omite el directorio {anio.get('Name', '')} porque no es un año válido[/yellow]")
                continue

            # Obtener el listado de archivos en el año
            remoto_origen_anio = f"{remoto_origen}/{anio['Name']}"
            console.print(f"Obteniendo archivos en [cyan]{remoto_origen_anio}[/cyan]...")
            result = subprocess.run(["rclone", "lsjson", remoto_origen_anio], capture_output=True, text=True, check=True)
            if result.returncode != 0:
                console.print(f"[red]Error en rclone:[/red] {result.returncode}")
                raise Exit(code=result.returncode)
            try:
                archivos = json.loads(result.stdout)
            except json.JSONDecodeError as error:
                console.print(f"[red]Error al decodificar JSON:[/red] {error}")
                raise Exit(code=1)

            # Bucle por cada archivo encontrado en el año
            for archivo in archivos:
                if archivo.get("IsDir") is True:
                    continue  # Si es un directorio, se omite
                origen_archivo = f"{remoto_origen_anio}/{archivo['Name']}"
                origen_tamano = archivo.get("Size", 0)

                # Separar las partes del nombre del archivo NNNNN-YYYY-DESC.pdf
                try:
                    archivo_nombre = archivo["Name"].split(".")[0]  # Obtener la parte del nombre sin la extensión
                    expediente_parts = archivo_nombre.split("-")
                    expediente_num = expediente_parts[0]
                    expediente_anio = expediente_parts[1]
                    descripcion = " ".join(expediente_parts[2:]) if len(expediente_parts) > 2 else ""
                except (IndexError, ValueError) as error:
                    console.print(f"[yellow]Falla al procesar el archivo:[/yellow] {origen_archivo} {error}")
                    continue

                # Validar que expediente_num sea un número de cinco dígitos y convertir a entero
                if not expediente_num.isdigit() or len(expediente_num) != 5:
                    console.print(f"[yellow]Número de expediente inválido en el archivo:[/yellow] {origen_archivo}")
                    continue
                expediente_num = int(expediente_num)

                # Validar que expediente_anio sea un número de cuatro dígitos y convertir a entero
                if not expediente_anio.isdigit() or len(expediente_anio) != 4:
                    console.print(f"[yellow]Año de expediente inválido en el archivo:[/yellow] {origen_archivo}")
                    continue
                expediente_anio = int(expediente_anio)

                # Consultar en la base de datos la posible existencia de esa digitalización
                posible_vsp_digitalizacion = (
                    db.query(VspDigitalizacion)
                    .join(Autoridad)
                    .filter(
                        Autoridad.id == autoridad.id,
                        VspDigitalizacion.expediente_anio == expediente_anio,
                        VspDigitalizacion.expediente_num == expediente_num,
                        VspDigitalizacion.descripcion == descripcion,
                    )
                    .first()
                )

                # Si YA existe, se omite
                if posible_vsp_digitalizacion:
                    contador_encontrados += 1
                    continue

                # Definir el nuevo nombre del archivo a UUID.pdf
                destino_dir = f"{autoridad.clave}/{expediente_anio}/"  # Observe que termina en / porque es un directorio

                # Ejecutar rclone para copiar el archivo al nuevo destino
                remoto_destino = (
                    f"{config.RCLONE_REMOTE_DESTINO}:/{config.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES}/{destino_dir}"
                )
                if save:
                    console.print(f"Copiando [cyan]{origen_archivo}[/cyan] -> [green]{remoto_destino}[/green]")
                    result = subprocess.run(["rclone", "--quiet", "copy", origen_archivo, remoto_destino])
                    if result.returncode != 0:
                        console.print(f"[red]Error en rclone al copiar:[/red] {origen_archivo} (código {result.returncode})")
                        raise Exit(code=result.returncode)
                else:
                    console.print(f"Simulando [cyan]{origen_archivo}[/cyan] -> [green]{remoto_destino}[/green]")

                # Definir el blob name (autoridad, año, archivo.pdf)
                blob_name = f"{destino_dir}{archivo['Name']}"  # Observe que no hay / porque destino_dir ya termina en /

                # Definir la URL pública del archivo copiado
                url_publica = f"https://storage.googleapis.com/{config.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES}/{blob_name}"

                # Insertar registro en la base de datos
                if save:
                    nueva_vsp_digitalizacion = VspDigitalizacion(
                        autoridad_id=autoridad.id,
                        expediente=f"{expediente_num}/{expediente_anio}",
                        expediente_anio=expediente_anio,
                        expediente_num=expediente_num,
                        descripcion=descripcion,
                        observaciones=None,
                        archivo=blob_name,
                        url=url_publica,
                    )
                    db.add(nueva_vsp_digitalizacion)
                    db.commit()

                # Agregar el reglón a la tabla
                tabla.add_row(
                    autoridad.clave,
                    f"{expediente_num}/{expediente_anio}",
                    descripcion,
                    str(origen_tamano),
                    blob_name,
                )
                contador_copiados += 1

    # Mostrar tabla
    console.print(tabla)

    if save:
        if contador_copiados:
            console.print(f"[bold green]Se copiaron {contador_copiados} archivos nuevos al bucket de destino.[/bold green]")
        if contador_encontrados:
            console.print(f"[yellow]Y se omitieron {contador_encontrados} archivos porque ya existen.[/yellow]")
    else:
        if contador_copiados:
            console.print(f"[cyan]Se podrían copiar {contador_copiados} archivos nuevos.[/cyan]")
        if contador_encontrados:
            console.print(f"[yellow]Y se encontraron {contador_encontrados} archivos ya existentes.[/yellow]")


@app.command()
def consultar(autoridad_clave: str = "", descripcion: str = "", offset: int = 0, limit: int = 10):
    """Consultar la tabla vsp_digitalizaciones"""
    console = Console()
    console.print("Consultando digitalizaciones...")

    # Inicializar la base de datos
    db = get_database()

    # Preparar consulta base
    stmt = select(
        Autoridad.clave,
        VspDigitalizacion.expediente,
        VspDigitalizacion.descripcion,
        VspDigitalizacion.archivo,
        VspDigitalizacion.creado,
    ).join(
        Autoridad,
    )

    # Si viene la autoridad_clave
    if autoridad_clave != "":
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)
        stmt = stmt.filter(Autoridad.clave.contains(autoridad_clave))

    # Si viene la descripción
    if descripcion != "":
        descripcion = safe_string(descripcion)
        if descripcion == "":
            console.print("[red]Descripción inválida[/red]")
            raise Exit(code=1)
        stmt = stmt.filter(VspDigitalizacion.descripcion.contains(descripcion))

    # Solo los que tengan estatus A
    stmt = stmt.filter(VspDigitalizacion.estatus == "A")
    stmt = stmt.order_by(VspDigitalizacion.descripcion).offset(offset).limit(limit)

    # Mostrar tabla
    tabla = Table(title="Digitalizaciones")
    tabla.add_column("Autoridad clave")
    tabla.add_column("Expediente")
    tabla.add_column("Descripción")
    tabla.add_column("Archivo (blob name)")
    tabla.add_column("Creado")
    for item in db.execute(stmt):
        tabla.add_row(
            item.clave,
            item.expediente,
            item.descripcion,
            item.archivo,
            item.creado.strftime("%Y-%m-%d %H:%M:%S"),
        )
    console.print(tabla)


@app.command()
def exportar(autoridad_clave: str = ""):
    """Exportar la tabla vsp_digitalizaciones a un archivo XLSX"""
    console = Console()
    console.print("Consultando digitalizaciones...")

    # Obtener configuración
    config = get_settings()

    # Inicializar la base de datos
    db = get_database()

    # Preparar consulta base
    stmt = select(
        Autoridad.clave,
        VspDigitalizacion.expediente,
        VspDigitalizacion.expediente_anio,
        VspDigitalizacion.expediente_num,
        VspDigitalizacion.descripcion,
        VspDigitalizacion.archivo,
        VspDigitalizacion.url,
    ).join(
        Autoridad,
    )

    # Si viene la autoridad_clave
    if autoridad_clave != "":
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)
        stmt = stmt.filter(Autoridad.clave.contains(autoridad_clave))

    # Solo los que tengan estatus A
    stmt = stmt.filter(VspDigitalizacion.estatus == "A")

    # Ordenar por clave de autoridad, año de expediente, número de expediente y descripción
    stmt = stmt.order_by(
        Autoridad.clave,
        VspDigitalizacion.expediente_anio,
        VspDigitalizacion.expediente_num,
        VspDigitalizacion.descripcion,
    )

    # Iniciar el archivo XLSX
    libro = Workbook()
    hoja = libro.active
    if hoja is None:
        console.print("[red]Error al crear la hoja de Excel[/red]")
        raise Exit(code=1)

    # Agregar la fila con las cabeceras de las columnas
    hoja.append(["Autoridad clave", "Expediente", "Año de expediente", "Número de expediente", "Descripción", "Archivo", "URL"])

    # Agregar los datos de las digitalizaciones
    contador = 0
    for item in db.execute(stmt):
        hoja.append(
            [
                item.clave,
                item.expediente,
                item.expediente_anio,
                item.expediente_num,
                item.descripcion,
                item.archivo,
                item.url,
            ]
        )
        contador += 1

    # Definir el nombre del archivo XLSX con la fecha y hora actual
    timezone = pytz.timezone(config.TZ)
    ahora_str = datetime.now(tz=timezone).strftime("%Y-%m-%d-%H%M%S")
    exportacion = Path("exports", f"vsp_digitalizaciones_{ahora_str}.xlsx")

    # Guardar el archivo XLSX
    try:
        libro.save(str(exportacion))
    except Exception as error:
        console.print(f"[red]Error al guardar el archivo Excel: {error}[/red]")
        raise Exit(code=1)

    # Mensaje de éxito
    if contador:
        console.print(f"[bold green]Se exportaron {contador} filas al archivo {exportacion.name}[/bold green]")
    else:
        console.print("[yellow]No se encontraron digitalizaciones para exportar. El archivo XLSX está vacío.[/yellow]")
