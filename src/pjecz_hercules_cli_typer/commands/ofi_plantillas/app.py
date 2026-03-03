"""
Oficios Plantillas command
"""

from typer import Typer

from typer import Exit, Option, Typer
from rich.console import Console
from rich.table import Table

from ...config.settings import get_settings
from ...models.autoridades import Autoridad
from ...models.ofi_plantillas import OfiPlantilla
from ...models.roles import Rol
from ...models.usuarios import Usuario
from ...models.usuarios_roles import UsuarioRol
from ...utils.database import get_database
from ...utils.safe_string import safe_clave, safe_string

app = Typer(help="Oficios Plantillas")


@app.command()
def query(autoridad_clave: str = "", usuario_email: str = "", offset: int = 0, limit: int = 10):
    """Consultar plantillas"""
    console = Console()
    console.print("Consultando plantillas...")

    # Consultar
    db = get_database()


@app.command()
def insert(autoridad_clave: str = "", usuario_email: str = "", offset: int = 0, limit: int = 10):
    """Crear plantilla"""
    console = Console()
    console.print("Crear plantilla...")

    # Consultar
    db = get_database()
