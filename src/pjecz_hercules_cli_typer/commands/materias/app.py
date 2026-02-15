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
def query(clave: str = "", offset: int = 0, limit: int = 10):
    """Consultar materias"""
    console = Console()
    console.print("Consultando materias...")

    # Consultar
    db = get_database()

    # Si NO viene la clave, se van a mostrar todas las materias
    if clave == "":
        tabla = Table(title="Materias")
        tabla.add_column("Clave", header_style="green", no_wrap=True)
        tabla.add_column("Nombre", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        for materia in db.query(Materia).order_by(Materia.clave).offset(offset).limit(limit).all():
            tabla.add_row(materia.clave, materia.nombre, materia.estatus)
        console.print(tabla)
        return

    # Si viene la clave
    clave = safe_clave(clave)
    if clave == "":
        console.print("[red]Clave inválida[/red]")
        return
    materias = db.query(Materia).filter(Materia.clave.contains(clave)).order_by(Materia.clave).offset(offset).limit(limit)
    if materias.count() == 0:
        console.print(f"[yellow]No se encontró una materia con la clave {clave}[/yellow]")
    elif materias.count() == 1:
        # Mostrar los detalles de una materia
        materia = materias.first()
        if materia is not None:
            console.print(f"[green]clave:[/green]   {materia.clave}")
            console.print(f"[green]nombre:[/green]  {materia.nombre}")
            console.print(f"[green]estatus:[/green] {materia.estatus}")
    else:
        # Mostrar tabla con todas las materias que coinciden con la clave
        tabla = Table(title="Materias")
        tabla.add_column("Clave", header_style="green", no_wrap=True)
        tabla.add_column("Nombre", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        for materia in materias.all():
            tabla.add_row(materia.clave, materia.nombre, materia.estatus)
        console.print(tabla)
