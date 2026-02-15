"""
Distritos command
"""

from typer import Typer
from rich.console import Console

from ...models.distritos import Distrito
from ...utils.database import get_database
from ...utils.safe_string import safe_clave

app = Typer(help="Distritos")


@app.command()
def query(clave: str):
    """Consultar un distrito por su clave"""
    console = Console()
    console.print(f"Consultando distrito con clave {clave}...")

    # Consultar
    db = get_database()
    clave = safe_clave(clave)
    if clave == "":
        console.print("[red]Clave inválida[/red]")
        return
    distrito = db.query(Distrito).filter(Distrito.clave == clave).first()

    # Mostrar
    if distrito is None:
        console.print(f"[yellow]No se encontró un distrito con la clave {clave}[/yellow]")
        return
    console.print(f"[green]clave:[/green]        {distrito.clave}")
    console.print(f"[green]nombre:[/green]       {distrito.nombre}")
    console.print(f"[green]nombre_corto:[/green] {distrito.nombre_corto}")
