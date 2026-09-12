"""
Edictos command
"""

from hashids import Hashids
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Typer

from pjecz_hercules_cli_typer.config.settings import get_settings
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.edictos import Edicto
from pjecz_hercules_cli_typer.utils.database import get_database
from pjecz_hercules_cli_typer.utils.google_cloud_storage import (
    check_file_exists_from_gcs,
    get_blob_name_from_url,
    public_blob_name,
    update_blob_name_in_gcs,
)
from pjecz_hercules_cli_typer.utils.safe_string import safe_clave, safe_string

app = Typer(help="Edictos")


@app.command()
def consultar(edicto_id: int = 0, autoridad_clave: str = "", offset: int = 0, limit: int = 40):
    """Consultar edictos"""
    console = Console()
    console.print("Consultando edictos...")

    # Inicializar la base de datos
    db = get_database()

    # Si viene edicto_id, consultar un edicto específico
    if edicto_id != 0:
        stmt = (
            select(
                Edicto.id,
                Autoridad.clave,
                Edicto.expediente,
                Edicto.descripcion,
                Edicto.estatus,
            )
            .join(
                Autoridad,
            )
            .where(
                Edicto.id == edicto_id,
            )
        )
        edicto = db.execute(stmt).first()
        if edicto is None:
            console.print(f"[yellow]No se encontró el edicto con ID {edicto_id}[/yellow]")
            raise Exit(code=1)
        if edicto is not None:
            console.print(f"ID: {edicto.id}")
            console.print(f"Autoridad: {edicto.autoridad.clave}")
            console.print(f"Expediente: {edicto.expediente}")
            console.print(f"Descripción: {edicto.descripcion}")
            console.print(f"Estatus: {edicto.estatus}")
            return Exit(code=0)

    # Preparar la consulta base
    stmt = select(
        Edicto.id,
        Autoridad.clave,
        Edicto.expediente,
        Edicto.descripcion,
        Edicto.estatus,
    ).join(
        Autoridad,
    ).offset(
        offset,
    ).limit(
        limit,
    )

    # Si viene autoridad_clave, filtrar los edictos por esa autoridad
    if autoridad_clave != "":
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        stmt = stmt.where(Autoridad.clave == autoridad_clave)

    # Mostrar tabla con los edictos
    tabla = Table(title=f"Edictos de la autoridad {autoridad_clave}")
    tabla.add_column("ID", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green")
    tabla.add_column("Expediente", header_style="green")
    tabla.add_column("Descripción", header_style="green")
    tabla.add_column("Estatus", header_style="green")
    for item in db.execute(stmt):
        tabla.add_row(str(item.id), item.clave, item.expediente, item.descripcion, item.estatus)
    console.print(tabla)

    # Consultar la cantidad total de edictos
    if autoridad_clave != "":
        total = db.query(Edicto).join(Autoridad).filter(Autoridad.clave == autoridad_clave).count()
    else:
        total = db.query(Edicto).count()
    console.print(f"[green]Total de edictos: {total}[/green]")


@app.command()
def validar(autoridad_clave: str = "", offset: int = 0, limit: int = 10, ciclar: bool = False):
    """Validar edictos, en particular que el url apunte a un recurso que exista en el depósito de edictos"""
    console = Console()
    console.print("Validando edictos...")

    # Obtener configuración
    settings = get_settings()

    # Validar que se haya configurado el depósito de edictos
    if settings.CLOUD_STORAGE_DEPOSITO_EDICTOS == "":
        console.print("[red]No se ha configurado el depósito de edictos[/red]")
        raise Exit(code=1)

    # Inicializar la base de datos
    db = get_database()

    # Si viene autoridad_clave
    autoridad = None
    if autoridad_clave != "":
        # Validar la clave de autoridad
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        # Validar que exista la autoridad
        autoridad = db.query(Autoridad).filter(Autoridad.clave == autoridad_clave).first()
        if autoridad is None:
            console.print(f"[red]No se encontró la autoridad con clave {autoridad_clave}[/red]")
            raise Exit(code=1)

    # Consultar la cantidad total de edictos
    if autoridad is not None:
        total = db.query(Edicto).join(Autoridad).filter(Edicto.autoridad_id == autoridad.id).filter(Edicto.estatus == "A").count()
    else:
        total = db.query(Edicto).count()

    # Si el total es cero, mostrar mensaje y salir
    if autoridad is not None and total == 0:
        console.print(f"[yellow]No se encontraron edictos para la autoridad {autoridad_clave}[/yellow]")
        raise Exit(code=1)
    if total == 0:
        console.print("[yellow]No se encontraron edictos[/yellow]")
        raise Exit(code=1)

    # Inicializar contadores
    total_fallidos = 0
    total_invalidos = 0
    total_validos = 0

    # Comenzar un bucle donde se va incrementando el offset hasta que no haya más edictos, si ciclar es True
    while True:
        edictos = db.query(Edicto)

        # Si viene la autoridad, filtrar los edictos por esa autoridad
        if autoridad is not None:
            edictos = edictos.filter(Edicto.autoridad_id == autoridad.id)

        # Terminar la consulta con estatus A, orden, offset y limit
        edictos = edictos.filter(Edicto.estatus == "A").order_by(Edicto.id.desc()).offset(offset).limit(limit)

        # Definir el título, si se filtra por una autoridad o no
        if autoridad is not None:
            titulo = f"Edictos de la autoridad {autoridad_clave} del {offset + 1} al {offset + limit} de {total}"
        else:
            titulo = f"Edictos del {offset + 1} al {offset + limit} de {total}"

        # Preparar la tabla
        tabla = Table(title=titulo)
        tabla.add_column("ID", header_style="white", no_wrap=True)
        tabla.add_column("Autoridad", header_style="white")
        tabla.add_column("URL", header_style="white")
        tabla.add_column("Válido", header_style="white")

        # Bucle con la barra de progreso
        with Progress() as progress:
            muestra = min(limit, total - offset)
            task = progress.add_task(f"Validando {muestra} edictos de la autoridad {autoridad_clave}", total=muestra)
            for edicto in edictos:
                # Validar que el url apunte a un recurso que exista en el depósito de edictos
                valido = False
                try:
                    valido = check_file_exists_from_gcs(
                        bucket_name=settings.CLOUD_STORAGE_DEPOSITO_EDICTOS,
                        blob_name=get_blob_name_from_url(edicto.url),
                    )
                except Exception as error:
                    total_fallidos += 1
                    console.print(f"[red]Error al validar el edicto {edicto.id}: {error}[/red]")
                    continue
                # Agregar renglon a la tabla
                if valido:
                    total_validos += 1
                    tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.url, "[green]Sí[/green]")
                else:
                    total_invalidos += 1
                    tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.url, "No", style="yellow")
                # Actualizar la barra de progreso
                progress.update(task, advance=1)

        # Mostrar la tabla
        console.print(tabla)

        # Si ciclar es False, salir del bucle
        if not ciclar:
            break

        # Incrementar el offset
        offset += limit

        # Si el offset es mayor o igual al total, salir del bucle
        if offset >= total:
            break

    # Mostrar los resultados finales
    if total_validos > 0:
        console.print(f"Total de edictos válidos: [green]{total_validos}[/green]")
    if total_invalidos > 0:
        console.print(f"Total de edictos inválidos: [yellow]{total_invalidos}[/yellow]")
    if total_fallidos > 0:
        console.print(f"Total de edictos fallidos: [red]{total_fallidos}[/red]")


@app.command()
def actualizar(autoridad_clave: str = "", offset: int = 0, limit: int = 10, ciclar: bool = False, guardar: bool = False):
    """Actualizar los edictos"""
    console = Console()
    if guardar:
        console.print("Actualizando edictos...")
    else:
        console.print("Mostrando los cambios que se podrían hacer en edictos...")

    # Obtener configuración
    settings = get_settings()
    hashids = Hashids(salt=settings.SALT, min_length=8)

    # Validar que se haya configurado el depósito de edictos
    if settings.CLOUD_STORAGE_DEPOSITO_EDICTOS == "":
        console.print("[red]No se ha configurado el depósito de edictos[/red]")
        raise Exit(code=1)

    # Inicializar la base de datos
    db = get_database()

    # Si viene autoridad_clave
    autoridad = None
    if autoridad_clave != "":
        # Validar la clave de autoridad
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        # Validar que exista la autoridad
        autoridad = db.query(Autoridad).filter(Autoridad.clave == autoridad_clave).first()
        if autoridad is None:
            console.print(f"[red]No se encontró la autoridad con clave {autoridad_clave}[/red]")
            raise Exit(code=1)

    # Consultar la cantidad total de edictos
    if autoridad is not None:
        total = db.query(Edicto).join(Autoridad).filter(Edicto.autoridad_id == autoridad.id).filter(Edicto.estatus == "A").count()
    else:
        total = db.query(Edicto).count()

    # Si el total es cero, mostrar mensaje y salir
    if autoridad is not None and total == 0:
        console.print(f"[yellow]No se encontraron edictos para la autoridad {autoridad_clave}[/yellow]")
        raise Exit(code=1)
    if total == 0:
        console.print("[yellow]No se encontraron edictos[/yellow]")
        raise Exit(code=1)

    # Inicializar contadores
    total_actualizados = 0
    total_fallidos = 0
    total_invalidos = 0
    total_sin_cambios = 0

    # Comenzar un bucle donde se va incrementando el offset hasta que no haya más edictos, si ciclar es True
    while True:
        edictos = db.query(Edicto)

        # Si viene la autoridad, filtrar los edictos por esa autoridad
        if autoridad is not None:
            edictos = edictos.filter(Edicto.autoridad_id == autoridad.id)

        # Terminar la consulta con estatus A, orden, offset y limit
        edictos = edictos.filter(Edicto.estatus == "A").order_by(Edicto.id.desc()).offset(offset).limit(limit)

        # Definir el título, si se filtra por una autoridad o no
        if autoridad is not None:
            titulo = f"Edictos de la autoridad {autoridad_clave} del {offset + 1} al {offset + limit} de {total}"
        else:
            titulo = f"Edictos del {offset + 1} al {offset + limit} de {total}"

        # Preparar la tabla
        tabla = Table(title=titulo)
        tabla.add_column("ID", header_style="white", no_wrap=True)
        tabla.add_column("Autoridad", header_style="white")
        tabla.add_column("URL", header_style="white")
        tabla.add_column("Válido", header_style="white")
        tabla.add_column("Actualizado", header_style="white")

        # Bucle con la barra de progreso
        with Progress() as progress:
            muestra = min(limit, total - offset)
            task = progress.add_task(f"Actualizando {muestra} edictos de la autoridad {autoridad_clave}", total=muestra)
            for edicto in edictos:
                # Validar que el url apunte a un recurso que exista en el depósito de edictos
                valido = False
                try:
                    valido = check_file_exists_from_gcs(
                        bucket_name=settings.CLOUD_STORAGE_DEPOSITO_EDICTOS,
                        blob_name=get_blob_name_from_url(edicto.url),
                    )
                except Exception as error:
                    total_fallidos += 1
                    console.print(f"[red]Error al validar el edicto {edicto.id}: {error}[/red]")
                    continue

                # Si NO es válido, agregar renglon a la tabla y continuar con el siguiente edicto
                if not valido:
                    total_invalidos += 1
                    tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.url, "No", "", style="yellow")
                    continue
                valido_str = "[green]Sí[/green]"

                # Conservar el url y el nombre del archivo anterior para compararlos después
                archivo_anterior = edicto.archivo
                url_anterior = edicto.url

                # Definir el URL correcto del archivo
                fecha = edicto.creado.date()
                descripcion = safe_string(edicto.descripcion, max_len=64, separator="-")
                hashed_id = str(hashids.encode(edicto.id))
                url_correcta = public_blob_name(
                    bucket_name=settings.CLOUD_STORAGE_DEPOSITO_EDICTOS,
                    base="",
                    distrito_clave=edicto.autoridad.distrito.clave,
                    autoridad_clave=edicto.autoridad.clave,
                    fecha=fecha,
                    descripcion=descripcion,
                    hashed_id=hashed_id,
                    extension="pdf",
                )

                # Obtener el nombre del archivo correcto a partir del URL correcto
                archivo_correcto = url_correcta.split("/")[-1]

                # Si hay cambios
                if url_anterior != url_correcta or archivo_anterior != archivo_correcto:
                    update_str = "Pendiente"
                    row_style = "cyan"
                    edicto.archivo = archivo_correcto
                    edicto.url = url_correcta
                    # Si guardar es True
                    if guardar:
                        # Mover el blob en Google Cloud Storage y actualizar la base de datos
                        try:
                            update_blob_name_in_gcs(
                                bucket_name=settings.CLOUD_STORAGE_DEPOSITO_EDICTOS,
                                old_blob_name=get_blob_name_from_url(url_anterior),
                                new_blob_name=get_blob_name_from_url(url_correcta),
                            )
                            db.add(edicto)
                            db.commit()
                            total_actualizados += 1
                            update_str = "Actualizado"
                            row_style = "green"
                        except Exception as error:
                            total_fallidos += 1
                            console.print(f"[red]Error al actualizar el blob en Google Cloud Storage: {error}[/red]")
                            continue
                    total_actualizados += 1
                    tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.url, valido_str, update_str, style=row_style)
                else:
                    total_sin_cambios += 1
                    tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.url, valido_str, "No", style="blue")

                # Actualizar la barra de progreso
                progress.update(task, advance=1)

        # Mostrar la tabla
        console.print(tabla)

        # Si ciclar es False, salir del bucle
        if not ciclar:
            break

        # Incrementar el offset
        offset += limit

        # Si el offset es mayor o igual al total, salir del bucle
        if offset >= total:
            break

    # Mostrar los resultados finales
    if guardar:
        if total_actualizados > 0:
            console.print(f"Total de edictos actualizados: [green]{total_actualizados}[/green]")
    else:
        if total_actualizados > 0:
            console.print(f"Total de edictos que se podrían actualizar: [green]{total_actualizados}[/green]")
    if total_invalidos > 0:
        console.print(f"Total de edictos inválidos: [yellow]{total_invalidos}[/yellow]")
    if total_fallidos > 0:
        console.print(f"Total de edictos fallidos: [red]{total_fallidos}[/red]")
    if total_sin_cambios > 0:
        console.print(f"Total de edictos sin cambios: [red]{total_sin_cambios}[/red]")
