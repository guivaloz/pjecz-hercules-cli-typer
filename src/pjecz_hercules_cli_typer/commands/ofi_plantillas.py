"""
Oficios Plantillas command
"""

from typing import Annotated

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Option, Typer

from ..models.autoridades import Autoridad
from ..models.ofi_plantillas import OfiPlantilla
from ..models.roles import Rol
from ..models.usuarios import Usuario
from ..models.usuarios_roles import UsuarioRol
from ..utils.database import get_database
from ..utils.safe_string import safe_clave, safe_email, safe_string

app = Typer(help="Oficios Plantillas")

GENERICO = """
<p style="text-align:right;">
    <strong>Oficio número [[FOLIO]]</strong><br>
    <strong>Saltillo, Coahuila., a [[DIA]] de [[MES]] del [[AÑO]]</strong>
</p>
<p>
    <strong>ATN. [[DESTINATARIOS]]</strong><br>
    <strong>PRESENTE.</strong>
</p>
<p>
    Por este conducto me permito hacer de su apreciable conocimiento que&nbsp;
</p>
<p>
    Si necesita más información, no dude en comunicarse con nosotros.
</p>
<p style="text-align:center;">
    <strong>A T E N T A M E N T E</strong>
</p>
<p style="text-align:center;">
    <strong>[[REMITENTE PUESTO]]</strong><br>
    <strong>[[REMITENTE AUTORIDAD]]</strong><br>
    <strong>PODER JUDICIAL DEL ESTADO DE COAHUILA DE ZARAGOZA</strong><br>
    <strong>(OFICIO FIRMADO ELECTRÓNICAMENTE)</strong>
</p>
<p style="text-align:center;">
    <strong>[[REMITENTE NOMBRE]]</strong>
</p>
"""


@app.command()
def query(autoridad_clave: str = "", descripcion: str = "", usuario_email: str = "", offset: int = 0, limit: int = 10):
    """Consultar oficios plantillas"""
    console = Console()
    console.print("Consultando oficios plantillas...")

    # Consultar
    db = get_database()

    # Preparar consulta base
    stmt = (
        select(
            OfiPlantilla.descripcion,
            Usuario.email,
            Usuario.puesto,
            Autoridad.clave,
            OfiPlantilla.destinatarios_emails,
            OfiPlantilla.esta_archivado,
            OfiPlantilla.esta_compartida,
        ).join(
            Usuario,
        ).join(
            Autoridad,
        )
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
        stmt = stmt.filter(OfiPlantilla.descripcion.contains(descripcion))

    # Si viene el usuario_email
    if usuario_email != "":
        usuario_email = safe_email(usuario_email, search_fragment=True)
        if usuario_email == "":
            console.print("[red]Email de usuario inválido[/red]")
            raise Exit(code=1)
        stmt = stmt.filter(Usuario.email.contains(usuario_email))

    # Solo los que tengan estatus A
    stmt = stmt.filter(OfiPlantilla.estatus == "A")
    stmt = stmt.order_by(OfiPlantilla.descripcion).offset(offset).limit(limit)

    # Mostrar tabla
    tabla = Table(title="Oficios Plantillas")
    tabla.add_column("Descripción")
    tabla.add_column("Usuario e-mail")
    tabla.add_column("Usuario puesto")
    tabla.add_column("Autoridad")
    tabla.add_column("Destinatarios")
    tabla.add_column("Arch.")
    tabla.add_column("Comp.")
    for item in db.execute(stmt):
        tabla.add_row(
            item.descripcion,
            item.email,
            item.puesto,
            item.clave,
            item.destinatarios_emails or "",
            "Sí" if item.esta_archivado else "",
            "Sí" if item.esta_compartida else "",
        )
    console.print(tabla)


@app.command()
def insert(
    autoridad_clave: str = "",
    usuario_email: str = "",
    offset: int = 0,
    limit: int = 10,
    save: Annotated[bool, Option("--save", "-s", help="Guardar cambios en la base de datos")] = False,
):
    """Crear una plantilla genérica para cada usuario con rol OFICIOS ESCRITOR u OFICIOS FIRMANTE"""
    console = Console()
    if save:
        console.print("Creando plantillas genéricas y guardando en la base de datos...")
    else:
        console.print("Mostrando los cambios que se podrían hacer...")

    # Consultar los usuarios
    db = get_database()
    usuarios = db.query(Usuario).join(UsuarioRol).join(Rol).join(Autoridad)

    # Filtrar que el puesto del usuario no sea vacío
    usuarios = usuarios.filter(Usuario.puesto != "")

    # Filtrar que el puesto del usuario no sea ND
    usuarios = usuarios.filter(Usuario.puesto != "ND")

    # Filtrar que la clave de la autoridad del usuario no sea ND
    usuarios = usuarios.filter(Autoridad.clave != "ND")

    # Filtrar el rol OFICIOS ESCRITOR u OFICIOS FIRMANTE
    usuarios = usuarios.filter(Rol.nombre.in_(["OFICIOS ESCRITOR", "OFICIOS FIRMANTE"]))

    # Filtrar que el estatus de UsuarioRol sea A
    usuarios = usuarios.filter(UsuarioRol.estatus == "A")

    # Si viene la autoridad_clave
    if autoridad_clave != "":
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)
        usuarios = usuarios.filter(Autoridad.clave.contains(autoridad_clave))

    # Si viene el usuario_email
    if usuario_email != "":
        usuario_email = safe_email(usuario_email, search_fragment=True)
        if usuario_email == "":
            console.print("[red]Email de usuario inválido[/red]")
            raise Exit(code=1)
        usuarios = usuarios.filter(Usuario.email.contains(usuario_email))

    # Solo los que tengan estatus A
    usuarios = usuarios.filter(Usuario.estatus == "A")

    # Terminar si no hay usuarios
    if usuarios.count() == 0:
        console.print("[yellow]No hay usuarios que coincidan con los filtros[/yellow]")
        raise Exit(code=0)

    # Preparar tabla
    tabla = Table(title="Oficios Plantillas que empiezan con GENERICO")
    tabla.add_column("Usuario e-mail")
    tabla.add_column("Usuario nombre")
    tabla.add_column("Usuario puesto")
    tabla.add_column("Autoridad")
    tabla.add_column("Descripción")
    tabla.add_column("Destinatarios")
    tabla.add_column("Arch.")
    tabla.add_column("Comp.")

    # Bucle por cada usuario
    for usuario in usuarios.order_by(Usuario.email).offset(offset).limit(limit).all():
        # Verificar si ya tiene una plantilla genérica
        plantillas_existentes = db.query(OfiPlantilla)
        plantillas_existentes = plantillas_existentes.filter(OfiPlantilla.usuario_id == usuario.id)
        plantillas_existentes = plantillas_existentes.filter(OfiPlantilla.descripcion.startswith('GENERICO'))
        plantillas_existentes = plantillas_existentes.filter(OfiPlantilla.estatus == "A")
        if plantillas_existentes.count() > 0:
            for plantilla_existente in plantillas_existentes.all():
                tabla.add_row(
                    usuario.email,
                    usuario.nombre,
                    usuario.puesto,
                    usuario.autoridad.clave,
                    plantilla_existente.descripcion,
                    plantilla_existente.destinatarios_emails or "",
                    "Sí" if plantilla_existente.esta_archivado else "",
                    "Sí" if plantilla_existente.esta_compartida else "",
                    style="blue",
                )
            continue

        # Definir contenido_html
        contenido_html = GENERICO

        # Reemplazar [[REMITENTE NOMBRE]] con el nombre del usuario
        contenido_html = contenido_html.replace("[[REMITENTE NOMBRE]]", usuario.nombre.upper())

        # Reemplazar [[REMITENTE PUESTO]] con el puesto del usuario
        contenido_html = contenido_html.replace("[[REMITENTE PUESTO]]", usuario.puesto.upper())

        # Reemplazar [[REMITENTE AUTORIDAD]] con la descripción de la autoridad del usuario
        contenido_html = contenido_html.replace("[[REMITENTE AUTORIDAD]]", usuario.autoridad.descripcion.upper())

        # Crear plantilla genérica
        ofi_plantilla = OfiPlantilla(
            usuario_id = usuario.id,
            descripcion = f"GENERICO {usuario.siglas}",
            destinatarios_emails = None,
            con_copias_emails = None,
            remitente_email = None,
            esta_archivado = False,
            esta_compartida = False,
            contenido_html = contenido_html,
            contenido_md = None,
            contenido_sfdt = None,
        )
        if save:
            db.add(ofi_plantilla)
            db.commit()

        # Agregar a la tabla
        tabla.add_row(
            usuario.email,
            usuario.nombre,
            usuario.puesto,
            usuario.autoridad.clave,
            ofi_plantilla.descripcion,
            ofi_plantilla.destinatarios_emails or "",
            "Sí" if ofi_plantilla.esta_archivado else "",
            "Sí" if ofi_plantilla.esta_compartida else "",
            style="green" if save else "white",
        )

    # Mostrar tabla
    console.print(tabla)
