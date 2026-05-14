"""
VASPEC Digitalizaciones command
"""

from typing import Annotated

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
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

    # Consultar
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
def insert(
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

    # Consultar
    db = get_database()

    # Si viene la autoridad_clave, consultarla
    autoridad = None
    if autoridad_clave != "":
        stmt = select(Autoridad.clave).where(Autoridad.clave == safe_clave(autoridad_clave))
        autoridad = db.execute(stmt).first()
        if autoridad is None:
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)

    # Si no viene la autoridad_clave, rastrear todas las digitalizaciones
    if autoridad is None:
        prefix = "cjc/"
    else:
        prefix = f"cjc/{autoridad.clave}/"

    # Rastrear archivos en el bucket de GCS
    try:
        blobs = get_blobs_from_gcs(settings.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES, prefix)
    except Exception as error:
        console.print(f"[red]Error al obtener los archivos del bucket de GCS: {error}[/red]")
        raise Exit(code=1)

    # Si save es False, mostrar los archivos que se podrían insertar
    if not save:
        tabla = Table(title="Digitalizaciones que se pueden insertar")
        tabla.add_column("Autoridad clave")
        tabla.add_column("Expediente")
        tabla.add_column("Descripción")
        for blob in blobs:
            # Se espera que cada blob sea CLAVE/AAAA/NNNN-AAAA-...pdf, donde...
            # - CLAVE es la clave de la autoridad,
            # - NNNN es el número en cuatro dígitos del expediente,
            # - AAAA es el año en cuatro dígitos del expediente,
            # - y el resto es la descripción
            try:
                if blob.name is None:
                    console.print(f"[yellow]Archivo sin nombre: {blob}[/yellow]")
                    continue
                parts = blob.name.split("/")
                if len(parts) < 3:
                    console.print(f"[yellow]Archivo con formato no válido: {blob}[/yellow]")
                    continue
                autoridad_clave = parts[0]
                expediente_part = parts[2].split(".")[0]  # Obtener la parte del nombre sin la extensión
                expediente_parts = expediente_part.split("-")
                if len(expediente_parts) < 2:
                    console.print(f"[yellow]Archivo con formato de expediente no válido: {blob.name}[/yellow]")
                    continue
                expediente_numero = expediente_parts[0]
                expediente_anio = expediente_parts[1]
                descripcion = " ".join(expediente_parts[2:]) if len(expediente_parts) > 2 else ""
                tabla.add_row(autoridad_clave, f"{expediente_numero}-{expediente_anio}", descripcion)
            except Exception as error:
                console.print(f"[yellow]Error al procesar el archivo {blob.name}: {error}[/yellow]")

        console.print(tabla)
        return

    # TODO: Insertar las digitalizaciones nuevas en la base de datos
    console.print("[yellow]Funcionalidad de inserción no implementada aún[/yellow]")
