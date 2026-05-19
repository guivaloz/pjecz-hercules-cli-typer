"""
VASPEC Digitalizaciones command
"""

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

    # Consultar
    db = get_database()

    # Si viene la autoridad_clave, consultarla
    autoridad = None
    if autoridad_clave != "":
        stmt = select(Autoridad.id, Autoridad.clave).where(Autoridad.clave == safe_clave(autoridad_clave))
        autoridad = db.execute(stmt).first()
        if autoridad is None:
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)

    # Si viene la autoridad_clave, rastrear solo esa, de lo contrario todas las digitalizaciones
    prefix = f"{settings.DIRECTORIO_VSP_DIGITALIZACIONES}/"
    title = "Digitalizaciones que se pueden insertar (todas las autoridades)"
    if autoridad:
        prefix = f"{prefix}{autoridad.clave.lower()}/"
        title = f"Digitalizaciones que se pueden insertar (autoridad: {autoridad.clave})"

    # Rastrear archivos en el bucket de GCS
    try:
        blobs = get_blobs_from_gcs(settings.CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES, prefix)
    except Exception as error:
        console.print(f"[red]Error al obtener los archivos del bucket de GCS: {error}[/red]")
        raise Exit(code=1)

    # Inicializar la tabla
    tabla = Table(title=title)
    tabla.add_column("Autoridad clave")
    tabla.add_column("Expediente")
    tabla.add_column("Descripción")

    # Procesar los archivos encontrados
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
            expediente_anio = int(expediente_parts[1])  # TODO: posible error al convertir a entero
        except IndexError as error:
            console.print(f"[yellow]Error al procesar el archivo {blob.name}: {error}[/yellow]")

        # Definir la descripcion
        descripcion = " ".join(expediente_parts[2:]) if len(expediente_parts) > 2 else ""

        # TODO: Consultar la autoridad
        if autoridad_clave == "":
            clave = autoridad_dir.upper()
            stmt = select(Autoridad).where(Autoridad.clave == clave)
            autoridad = db.execute(stmt).first()
            if autoridad is None:
                console.print(f"[yellow]Se omite el archivo {blob.name} porque no existe la autoridad {clave}[/yellow]")
                continue

        # Consultar en la base de datos la existencia
        stmt = (
            select(
                VspDigitalizacion.id,
            )
            .join(
                Autoridad,
            )
            .where(
                Autoridad.clave == autoridad_clave,
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
            stmt = insert(VspDigitalizacion).values(
                autoridad_id=autoridad.id,
                expediente=f"{expediente_num}/{expediente_anio}",
                expediente_anio=expediente_anio,
                expediente_num=expediente_num,
                descripcion=descripcion,
                observaciones=None,
                archivo=blob.name,
                url=blob.public_url,
                tamano=None,
                tiempo=None,
            )
            db.execute(stmt)

        # Agregar el reglón a la tabla
        tabla.add_row(autoridad_clave, f"{expediente_num}/{expediente_anio}", descripcion)

    # Mostrar tabla
    console.print(tabla)
    return
