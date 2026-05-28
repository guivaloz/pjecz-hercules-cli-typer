"""
VASPEC Digitalizaciones command
"""

import subprocess
from typing import Annotated

from rich.console import Console
from rich.table import Table
from sqlalchemy import insert, select
from typer import Exit, Option, Typer

from pjecz_hercules_cli_typer.config.settings import get_settings
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.vsp_digitalizaciones import VspDigitalizacion
from pjecz_hercules_cli_typer.utils.database import get_database
from pjecz_hercules_cli_typer.utils.google_cloud_storage import get_blobs_from_gcs
from pjecz_hercules_cli_typer.utils.safe_string import safe_clave, safe_string

app = Typer(help="VASPEC Digitalizaciones")


@app.command()
def query(autoridad_clave: str = "", descripcion: str = "", offset: int = 0, limit: int = 10):
    """Consultar digitalizaciones"""
    console = Console()
    console.print("Consultando digitalizaciones...")

    # Inicializar la base de datos
    db = get_database()

    # Preparar consulta base
    stmt = select(
        Autoridad.clave,
        VspDigitalizacion.expediente,
        VspDigitalizacion.descripcion,
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
    tabla.add_column("Creado")
    for item in db.execute(stmt):
        tabla.add_row(
            item.clave,
            item.expediente,
            item.descripcion,
            item.cleado,
        )
    console.print(tabla)


@app.command()
def add(
    autoridad_clave: str = "",
    save: Annotated[bool, Option("--save", "-s", help="Guardar cambios en la base de datos")] = False,
):
    """Insertar digitalizaciones rastreando los archivos nuevos en el bucket de GCS"""
    console = Console()
    if save:
        console.print("Insertando digitalizaciones en la base de datos...")
    else:
        console.print("Mostrando las inserciones que se podrían hacer...")

    # Obtener configuración
    settings = get_settings()

    # Validar que se haya configurado el depósito de digitaliaciones
    if settings.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES == "":
        console.print("[red]No se ha configurado el depósito de edictos[/red]")
        raise Exit(code=1)

    # Inicializar la base de datos
    db = get_database()

    # Si viene la autoridad_clave, consultarla
    autoridad = None
    if autoridad_clave != "":
        stmt = select(Autoridad).where(Autoridad.clave == safe_clave(autoridad_clave))
        autoridad = db.execute(stmt).scalar_one_or_none()
        if autoridad is None:
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)

    # Si viene la autoridad_clave, rastrear solo esa, de lo contrario todas las digitalizaciones
    prefix = f"{settings.DIRECTORIO_VSP_DIGITALIZACIONES}/" if settings.DIRECTORIO_VSP_DIGITALIZACIONES != "" else ""
    title = "Digitalizaciones que se pueden insertar (todas las autoridades)"
    if autoridad:
        prefix = f"{prefix}{autoridad.clave.lower()}/"
        title = f"Digitalizaciones que se pueden insertar (autoridad: {autoridad.clave})"
    console.print(f"Rastreando archivos en el bucket de GCS con prefijo [cyan]{prefix}[/cyan]...")

    # Rastrear archivos en el bucket de GCS
    try:
        blobs = get_blobs_from_gcs(settings.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES, prefix)
    except Exception as error:
        console.print(f"[red]Error al obtener los archivos del bucket de GCS: {error}[/red]")
        raise Exit(code=1)

    # Si no se encontraron archivos, salir
    if not blobs:
        console.print("[yellow]No se encontraron archivos en el bucket de GCS[/yellow]")
        return

    # Inicializar la tabla
    tabla = Table(title=title)
    tabla.add_column("Autoridad clave")
    tabla.add_column("Expediente")
    tabla.add_column("Descripción")

    # Procesar los archivos encontrados
    contador = 0
    clave = ""  # Para consultar la clave de la autoridad si cambia
    for blob in blobs:
        if blob.name is None:
            console.print(f"[yellow]Archivo sin nombre: {blob}[/yellow]")
            continue

        # Se espera que cada blob sea CLAVE/AAAA/NNNNN-AAAA-...pdf, donde...
        # - CLAVE es la clave de la autoridad,
        # - NNNNN es el número en cinco dígitos del expediente,
        # - AAAA es el año en cuatro dígitos del expediente,
        # - y el resto es la descripción
        try:
            # Separar las partes de derecha a izquierda /AUTORIDAD_DIR/ANIO/ARCHIVO
            parts = blob.name.split("/")
            archivo_part = parts[-1]
            anio_part = parts[-2]
            autoridad_dir = parts[-3]
            # Separar las partes del nombre del archivo NNNNN-YYYY-DESC.pdf
            archivo_nombre = archivo_part.split(".")[0]  # Obtener la parte del nombre sin la extensión
            expediente_parts = archivo_nombre.split("-")
            expediente_num = expediente_parts[0]
            expediente_anio = expediente_parts[1]
            descripcion = " ".join(expediente_parts[2:]) if len(expediente_parts) > 2 else ""
        except (IndexError, ValueError) as error:
            console.print(f"[yellow]Error al procesar el archivo {blob.name}: {error}[/yellow]")
            continue

        # Validar que expediente_num sea un número de cinco dígitos y convertir a entero
        if not expediente_num.isdigit() or len(expediente_num) != 5:
            console.print(f"[yellow]Número de expediente inválido en el archivo {blob.name}[/yellow]")
            continue
        expediente_num = int(expediente_num)

        # Validar que expediente_anio sea un número de cuatro dígitos y convertir a entero
        if not expediente_anio.isdigit() or len(expediente_anio) != 4:
            console.print(f"[yellow]Año de expediente inválido en el archivo {blob.name}[/yellow]")
            continue
        expediente_anio = int(expediente_anio)

        # Consultar la autoridad
        clave = autoridad_dir.upper()
        if autoridad is None or autoridad_clave == "" or autoridad_clave != clave:
            stmt = select(Autoridad).where(Autoridad.clave == clave)
            autoridad = db.execute(stmt).scalar_one_or_none()
            if autoridad is None:
                console.print(f"[yellow]Se omite el archivo {blob.name} porque no existe la autoridad {clave}[/yellow]")
                continue
            clave = autoridad.clave

        # Consultar en la base de datos la existencia
        stmt = (
            select(
                VspDigitalizacion.id,
            )
            .join(
                Autoridad,
            )
            .where(
                Autoridad.id == autoridad.id,
                VspDigitalizacion.expediente_anio == expediente_anio,
                VspDigitalizacion.expediente_num == expediente_num,
                VspDigitalizacion.descripcion == descripcion,
            )
        )
        posible_vsp_digitalizacion = db.execute(stmt).first()

        # Si YA existe, se omite
        if posible_vsp_digitalizacion:
            continue

        # Insertar
        if save:
            vsp_digitalizacion = VspDigitalizacion(
                autoridad_id=autoridad.id,
                expediente=f"{expediente_num}/{expediente_anio}",
                expediente_anio=expediente_anio,
                expediente_num=expediente_num,
                descripcion=descripcion,
                observaciones=None,
                archivo=blob.name,
                url=blob.public_url,
                tamano=blob.size,
                tiempo=blob.updated,
            )
            db.add(vsp_digitalizacion)
            db.commit()
            contador += 1

        # Agregar el reglón a la tabla
        tabla.add_row(clave, f"{expediente_num}/{expediente_anio}", descripcion)

    # Mostrar tabla
    console.print(tabla)

    # Mostrar el contador de inserciones
    if save:
        console.print(f"[bold green]Se insertaron {contador} digitalizaciones en la base de datos.[/bold green]")


@app.command()
def copy(
    save: Annotated[bool, Option("--save", "-s", help="Guardar cambios en la base de datos")] = False,
):
    """Copiar archivos del bucket pjecz-cetus al bucket pjecz-aquarius con rclone"""
    console = Console()
    if save:
        console.print("Ejecutando los comandos para copiar entre buckets...")
    else:
        console.print("Mostrando los comandos para copiar entre buckets...")

    # Inicializar la base de datos
    db = get_database()

    # Consultar las autoridades donde es_vsp_digitalizaciones es True
    stmt = select(Autoridad.clave).where(Autoridad.es_vsp_digitalizaciones).order_by(Autoridad.clave)
    autoridades = db.execute(stmt).all()
    if autoridades is None:
        console.print("[yellow]No se encontraron autoridades con digitalizaciones[/yellow]")
        return

    # Inicializar listado con las copias a realizar, cada elemento es una tupla (origen, destino)
    copias = []
    for autoridad in autoridades:
        copias.append(
            (
                f"googlestoragevaspec:/pjecz-cetus/cjc/{autoridad.clave.lower()}",
                f"googlestoragejusticiadigital:/pjecz-aquarius/{autoridad.clave.lower()}",
            )
        )

    for origen, destino in copias:
        console.print(f"Copiando [cyan]{origen}[/cyan] -> [green]{destino}[/green]")
        if save:
            result = subprocess.run(["rclone", "--progress", "copy", origen, destino])
            if result.returncode != 0:
                console.print(f"[red]Error al copiar {origen} (código {result.returncode})[/red]")
                raise Exit(code=result.returncode)

    if save:
        console.print("[bold green]Copia completada.[/bold green]")
