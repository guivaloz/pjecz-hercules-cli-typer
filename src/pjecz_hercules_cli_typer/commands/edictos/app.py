"""
Edictos command
"""

from typing import Annotated

from hashids import Hashids
from typer import Exit, Option, Typer
from rich.console import Console
from rich.table import Table

from ...config.settings import get_settings
from ...models.autoridades import Autoridad
from ...models.edictos import Edicto
from ...utils.database import get_database
from ...utils.google_cloud_storage import check_file_exists_from_gcs, get_blob_name_from_url, public_blob_name, update_blob_name_in_gcs
from ...utils.safe_string import safe_clave, safe_string

app = Typer(help="Edictos")


@app.command()
def query(edicto_id: int = 0, autoridad_clave: str = "", offset: int = 0, limit: int = 10):
    """Consultar edictos"""
    console = Console()
    console.print("Consultando edictos...")

    # Consultar
    db = get_database()

    # Si se especificó un ID, consultar un edicto
    if edicto_id:
        edicto = db.query(Edicto).get(edicto_id)
        if edicto:
            console.print(f"ID: {edicto.id}")
            console.print(f"Autoridad: {edicto.autoridad.clave}")
            console.print(f"Expediente: {edicto.expediente}")
            console.print(f"Descripción: {edicto.descripcion}")
            console.print(f"Estatus: {edicto.estatus}")
        else:
            console.print(f"No se encontró el edicto con ID {edicto_id}")
        return

    # Si se especificó una clave de autoridad, consultar los edictos de esa autoridad
    if autoridad_clave:
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        edictos = db.query(Edicto).join(Autoridad).filter(Autoridad.clave == autoridad_clave).order_by(Edicto.id.desc()).offset(offset).limit(limit)
        if edictos.count() == 0:
            console.print(f"[yellow]No se encontraron edictos para la autoridad {autoridad_clave}[/yellow]")
            raise Exit(code=1)
        else:
            tabla = Table(title=f"Edictos de la autoridad {autoridad_clave}")
            tabla.add_column("ID", header_style="green", no_wrap=True)
            tabla.add_column("Autoridad", header_style="green")
            tabla.add_column("Expediente", header_style="green")
            tabla.add_column("Descripción", header_style="green")
            tabla.add_column("Estatus", header_style="green")
            for edicto in edictos.limit(limit).all():
                tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.expediente, edicto.descripcion, edicto.estatus)
            console.print(tabla)
        return

    # Consultar los edictos más recientes
    edictos = db.query(Edicto).order_by(Edicto.id.desc()).offset(offset).limit(limit)
    if edictos.count() == 0:
        console.print("[yellow]No se encontraron edictos[/yellow]")
    else:
        tabla = Table(title="Edictos más recientes")
        tabla.add_column("ID", header_style="green", no_wrap=True)
        tabla.add_column("Autoridad", header_style="green")
        tabla.add_column("Expediente", header_style="green")
        tabla.add_column("Descripción", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        for edicto in edictos.all():
            tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.expediente, edicto.descripcion, edicto.estatus)
        console.print(tabla)


@app.command()
def update(
    autoridad_clave: str = "",
    offset: int = 0,
    limit: int = 10,
    all: Annotated[bool, Option("--all", "-a", help="Todos los registros")] = False,
    save: Annotated[bool, Option("--save", "-s", help="Guardar cambios en la base de datos")] = False,
):
    """Actualizar los edictos"""
    console = Console()
    if save:
        console.print("Actualizando edictos...")
    else:
        console.print("Mostrando los cambios que se podrían hacer...")

    # Obtener configuración
    settings = get_settings()
    hashids = Hashids(salt=settings.SALT, min_length=8)

    # Validar que se haya configurado el depósito de edictos
    if settings.CLOUD_STORAGE_DEPOSITO_EDICTOS == "":
        console.print("[red]No se ha configurado el depósito de edictos[/red]")
        raise Exit(code=1)

    # Consultar
    db = get_database()

    # Si se especificó una clave de autoridad
    if autoridad_clave:
        # Consultar los edictos de esa autoridad
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        edictos = db.query(Edicto).join(Autoridad).filter(Autoridad.clave == autoridad_clave).order_by(Edicto.id.desc()).offset(offset).limit(limit)
        if edictos.count() == 0:
            console.print(f"[yellow]No se encontraron edictos para la autoridad {autoridad_clave}[/yellow]")
            raise Exit(code=1)
        total = db.query(Edicto).join(Autoridad).filter(Autoridad.clave == autoridad_clave).count()
        title = f"Hay {total} edictos en la autoridad {autoridad_clave}"
    else:
        # Consultar los edictos más recientes
        edictos = db.query(Edicto).order_by(Edicto.id.desc()).offset(offset).limit(limit)
        if edictos.count() == 0:
            console.print("[yellow]No se encontraron edictos[/yellow]")
            raise Exit(code=1)
        total = db.query(Edicto).count()
        title = f"Hay {total} edictos en total"

    # Inicializar contadores
    total_actualizados = 0
    total_sin_cambios = 0

    # Bucle para incrementar el offset hasta que no haya más edictos
    while edictos.count() > 0:
        # Mostrar tabla
        tabla = Table(title=f"{title}; mostrando del {offset + 1} al {offset + limit}")
        tabla.add_column("ID", header_style="green", no_wrap=True)
        tabla.add_column("Autoridad", header_style="green")
        tabla.add_column("Archivo anterior", header_style="green")
        tabla.add_column("Archivo nuevo", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        # Primer bucle para validar
        contador = 0
        for edicto in edictos.all():
            hay_cambios = False
            # Definir el nombre del archivo como YYYY-MM-DD-DESCRIPCION-HASHID.pdf
            fecha = edicto.creado.date()
            descripcion = safe_string(edicto.descripcion, max_len=64, separator="-")
            hashed_id = str(hashids.encode(edicto.id))
            archivo_correcto = f"{fecha.isoformat()}-{descripcion}-{hashed_id}.pdf"
            # Cambiar el nombre del archivo
            archivo_anterior = edicto.archivo
            if archivo_anterior != archivo_correcto:
                edicto.archivo = archivo_correcto
                hay_cambios = True
            # Cambiar el URL del archivo
            url_anterior = edicto.url
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
            if url_anterior != url_correcta:
                edicto.url = url_correcta
                hay_cambios = True
            # Por defecto el renglon es azul
            style="blue"
            # Si hay cambios
            if hay_cambios:
                try:
                    if check_file_exists_from_gcs(
                        bucket_name=settings.CLOUD_STORAGE_DEPOSITO_EDICTOS,
                        blob_name=get_blob_name_from_url(url_anterior),
                    ):
                        style="green"
                    else:
                        style="red"
                except Exception as e:
                    console.print(f"[red]Error al verificar si el archivo existe en Google Cloud Storage: {e}[/red]")
                    continue
            # Agregar renglon a la tabla
            tabla.add_row(str(edicto.id), edicto.autoridad.clave, archivo_anterior, edicto.archivo, edicto.estatus, style=style)
            # Si el style NO es green, pasar al siguiente edicto sin actualizar
            if style != "green":
                total_sin_cambios += 1
                continue
            # Si save es verdadero, mover el blob en Google Cloud Storage y actualizar el URL en la base de datos
            if save:
                try:
                    update_blob_name_in_gcs(
                        bucket_name=settings.CLOUD_STORAGE_DEPOSITO_EDICTOS,
                        old_blob_name=get_blob_name_from_url(url_anterior),
                        new_blob_name=get_blob_name_from_url(url_correcta),
                    )
                    db.add(edicto)
                    contador += 1
                except Exception as e:
                    console.print(f"[red]Error al actualizar el blob en Google Cloud Storage: {e}[/red]")
                    continue
        # Guardar los cambios en la base de datos
        if contador > 0:
            # console.print(f"[green]Guardando {contador} cambios en la base de datos[/green]")
            db.commit()
            total_actualizados += contador
        # Mostrar la tabla
        console.print(tabla)
        # Si no se especificó la opción --all, salir del ciclo
        if not all:
            break
        # Incrementar el offset
        offset += limit
        # Consultar los siguientes edictos
        if autoridad_clave:
            edictos = db.query(Edicto).join(Autoridad).filter(Autoridad.clave == autoridad_clave).order_by(Edicto.id.desc()).offset(offset).limit(limit)
        else:
            edictos = db.query(Edicto).order_by(Edicto.id.desc()).offset(offset).limit(limit)

    # Mostrar los contadores
    if total_actualizados > 0:
        console.print(f"[green]Total actualizados: {total_actualizados}[/green]")
    if total_sin_cambios > 0:
        console.print(f"[blue]Total sin cambios: {total_sin_cambios}[/blue]")
