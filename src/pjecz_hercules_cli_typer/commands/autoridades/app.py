"""
Autoridades command
"""

from typer import Typer
from rich.console import Console

from ...models.autoridades import Autoridad
from ...utils.database import get_database
from ...utils.safe_string import safe_clave

app = Typer(help="Autoridades")


@app.command()
def query(clave: str):
    """Consultar una autoridad por su clave"""
    console = Console()
    console.print(f"Consultando autoridad con clave {clave}...")

    # Consultar
    db = get_database()
    clave = safe_clave(clave)
    if clave == "":
        console.print("[red]Clave inválida[/red]")
        return
    autoridad = db.query(Autoridad).filter(Autoridad.clave == clave).first()

    # Mostrar
    if autoridad is None:
        console.print(f"[yellow]No se encontró una autoridad con la clave {clave}[/yellow]")
        return
    console.print(f"[green]clave:[/green]             {autoridad.clave}")
    console.print(f"[green]descripcion:[/green]       {autoridad.descripcion}")
    console.print(f"[green]descripcion_corta:[/green] {autoridad.descripcion_corta}")
