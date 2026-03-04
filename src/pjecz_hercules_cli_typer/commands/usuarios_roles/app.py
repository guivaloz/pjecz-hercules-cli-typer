"""
Usuarios-Roles command
"""

from typer import Typer

from typer import Exit
from rich.console import Console
from rich.table import Table

from ...models.autoridades import Autoridad
from ...models.roles import Rol
from ...models.usuarios import Usuario
from ...models.usuarios_roles import UsuarioRol
from ...utils.database import get_database
from ...utils.safe_string import safe_clave, safe_email, safe_string

app = Typer(help="Usuarios-Roles")


@app.command()
def query(autoridad_clave: str = "", rol_nombre: str = "", usuario_email: str = "", offset: int = 0, limit: int = 10):
    """Consultar usuarios_roles"""
    console = Console()
    console.print("Consultando usuarios_roles...")

    # Consultar
    db = get_database()
    usuarios_roles = db.query(UsuarioRol).join(Rol).join(Usuario).join(Autoridad)

    # Si viene la autoridad_clave
    if autoridad_clave != "":
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave de autoridad inválida[/red]")
            raise Exit(code=1)
        usuarios_roles = usuarios_roles.filter(Autoridad.clave.contains(autoridad_clave))

    # Si viene el usuario_email
    if usuario_email != "":
        usuario_email = safe_email(usuario_email, search_fragment=True)
        if usuario_email == "":
            console.print("[red]Email de usuario inválido[/red]")
            raise Exit(code=1)
        usuarios_roles = usuarios_roles.filter(Usuario.email.contains(usuario_email))

    # Si viene el rol_nombre
    if rol_nombre != "":
        rol_nombre = safe_string(rol_nombre)
        if rol_nombre == "":
            console.print("[red]Nombre de rol inválido[/red]")
            raise Exit(code=1)
        usuarios_roles = usuarios_roles.filter(Rol.nombre.contains(rol_nombre))

    # Solo los que tengan estatus A
    usuarios_roles = usuarios_roles.filter(Usuario.estatus == "A")

    # Determinar la cantidad total de registros que coinciden con los filtros
    total = usuarios_roles.count()

    # Mostrar tabla
    tabla = Table(title=f"Hay {total} Usuarios-Roles")
    tabla.add_column("ID", header_style="green", no_wrap=True)
    tabla.add_column("Rol nombre", header_style="green")
    tabla.add_column("Usuario email", header_style="green")
    tabla.add_column("Usuario nombre", header_style="green")
    tabla.add_column("Autoridad", header_style="green")
    tabla.add_column("Usuario puesto", header_style="green")
    for usuario_rol in usuarios_roles.order_by(Usuario.email).offset(offset).limit(limit).all():
        tabla.add_row(str(usuario_rol.id), usuario_rol.rol.nombre, usuario_rol.usuario.email, usuario_rol.usuario.nombre, usuario_rol.usuario.autoridad.clave, usuario_rol.usuario.puesto)
    console.print(tabla)
