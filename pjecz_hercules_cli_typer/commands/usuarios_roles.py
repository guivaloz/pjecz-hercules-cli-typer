"""
Usuarios-Roles command
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Typer

from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.roles import Rol
from pjecz_hercules_cli_typer.models.usuarios import Usuario
from pjecz_hercules_cli_typer.models.usuarios_roles import UsuarioRol
from pjecz_hercules_cli_typer.utils.database import get_database
from pjecz_hercules_cli_typer.utils.safe_string import safe_clave, safe_email, safe_string

app = Typer(help="Usuarios-Roles")


@app.command()
def query(autoridad_clave: str = "", rol_nombre: str = "", usuario_email: str = "", offset: int = 0, limit: int = 10):
    """Consultar usuarios_roles"""
    console = Console()
    console.print("Consultando usuarios_roles...")

    # Consultar
    db = get_database()

    # Preparar consulta base
    stmt = (
        select(
            UsuarioRol.id,
            Rol.nombre,
            Usuario.email,
            Autoridad.clave,
            Usuario.puesto,
        )
        .join(
            Rol,
        )
        .join(
            Usuario,
        )
        .join(
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

    # Si viene el usuario_email
    if usuario_email != "":
        usuario_email = safe_email(usuario_email, search_fragment=True)
        if usuario_email == "":
            console.print("[red]Email de usuario inválido[/red]")
            raise Exit(code=1)
        stmt = stmt.filter(Usuario.email.contains(usuario_email))

    # Si viene el rol_nombre
    if rol_nombre != "":
        rol_nombre = safe_string(rol_nombre)
        if rol_nombre == "":
            console.print("[red]Nombre de rol inválido[/red]")
            raise Exit(code=1)
        stmt = stmt.filter(Rol.nombre.contains(rol_nombre))

    # Solo los que tengan estatus A
    stmt = stmt.filter(Usuario.estatus == "A")
    stmt = stmt.order_by(Usuario.email).offset(offset).limit(limit)

    # Mostrar tabla
    tabla = Table(title="Usuarios-Roles")
    tabla.add_column("ID", header_style="green", no_wrap=True)
    tabla.add_column("Rol nombre", header_style="green")
    tabla.add_column("Usuario email", header_style="green")
    tabla.add_column("Usuario nombre", header_style="green")
    tabla.add_column("Autoridad", header_style="green")
    tabla.add_column("Usuario puesto", header_style="green")
    for item in db.execute(stmt):
        tabla.add_row(
            str(item.id),
            item.nombre,
            item.email,
            item.nombre,
            item.clave,
            item.puesto,
        )
    console.print(tabla)
