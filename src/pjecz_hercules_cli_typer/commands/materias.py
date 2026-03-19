"""
Materias command
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Typer

from ..models.materias import Materia
from ..utils.database import get_database
from ..utils.safe_string import safe_clave

app = Typer(help="Materias")


@app.command()
def query(clave: str = "", offset: int = 0, limit: int = 10):
    """Consultar materias"""
    console = Console()
    console.print("Consultando materias...")

    # Consultar
    db = get_database()

    # Si viene la clave
    if clave != "":
        # Consultar una materia específica
        clave = safe_clave(clave)
        if clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        stmt = (
            select(
                Materia.clave,
                Materia.nombre,
                Materia.estatus,
            ).where(Materia.clave == clave)
        )
        materia = db.execute(stmt).first()
        if materia is None:
            console.print(f"[yellow]No se encontró una materia con la clave {clave}[/yellow]")
            raise Exit(code=1)
        console.print(f"[green]clave:[/green]   {materia.clave}")
        console.print(f"[green]nombre:[/green]  {materia.nombre}")
        console.print(f"[green]estatus:[/green] {materia.estatus}")
        return Exit(code=0)

    # De lo contrario, consultar todas las materias
    stmt = (
        select(
            Materia.clave,
            Materia.nombre,
            Materia.estatus,
        ).order_by(Materia.clave).offset(offset).limit(limit)
    )
    tabla = Table(title="Materias")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Nombre", header_style="green")
    tabla.add_column("Estatus", header_style="green")
    for item in db.execute(stmt):
        tabla.add_row(item.clave, item.nombre, item.estatus)
    console.print(tabla)
