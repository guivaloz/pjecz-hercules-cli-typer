"""
Materias command
"""

from typer import Typer
from rich.console import Console
from rich.table import Table

from ...models.materias import Materia
from ...utils.database import get_database
from ...utils.safe_string import safe_clave

app = Typer(help="Materias")


@app.command()
def query(clave: str = "", limit: int = 10):
    """Consultar una materia por su clave"""
    console = Console()
    console.print(f"Consultando materia con clave {clave}...")

    # Consultar
    db = get_database()

    # Si viene la clave, se va a consultar solo esa materia
    if clave != "":
        clave = safe_clave(clave)
        if clave == "":
            console.print("[red]Clave inválida[/red]")
            return
        materia = db.query(Materia).filter(Materia.clave == clave).first()
        if materia is None:
            console.print(f"[yellow]No se encontró una materia con la clave {clave}[/yellow]")
            return
        console.print(f"[green]clave:[/green]   {materia.clave}")
        console.print(f"[green]nombre:[/green]  {materia.nombre}")
        console.print(f"[green]estatus:[/green] {materia.estatus}")
        return

    # De lo contrario, se van a mostrar todas las materias
    tabla = Table(title="Materias")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Nombre", header_style="green")
    tabla.add_column("Estatus", header_style="green")
    for materia in db.query(Materia).limit(limit).all():
        tabla.add_row(materia.clave, materia.nombre, materia.estatus)
    console.print(tabla)
