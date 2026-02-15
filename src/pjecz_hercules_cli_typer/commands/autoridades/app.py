"""
Autoridades command
"""

from typer import Typer
from rich.console import Console
from rich.table import Table

from ...models.autoridades import Autoridad
from ...utils.database import get_database
from ...utils.safe_string import safe_clave

app = Typer(help="Autoridades")


@app.command()
def query(clave: str = "", offset: int = 0, limit: int = 10):
    """Consultar autoridades"""
    console = Console()
    console.print("Consultando autoridades...")

    # Consultar
    db = get_database()

    # Si NO viene la clave, se van a mostrar todas las autoridades
    if clave == "":
        tabla = Table(title="Autoridades")
        tabla.add_column("Clave", header_style="green", no_wrap=True)
        tabla.add_column("Descripción", header_style="green")
        tabla.add_column("Descripción corta", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        for autoridad in db.query(Autoridad).order_by(Autoridad.clave).offset(offset).limit(limit).all():
            tabla.add_row(autoridad.clave, autoridad.descripcion, autoridad.descripcion_corta, autoridad.estatus)
        console.print(tabla)
        return

    # Si viene la clave
    clave = safe_clave(clave)
    if clave == "":
        console.print("[red]Clave inválida[/red]")
        return
    autoridades = db.query(Autoridad).filter(Autoridad.clave.contains(clave)).order_by(Autoridad.clave).offset(offset).limit(limit)
    if autoridades.count() == 0:
        console.print(f"[yellow]No se encontró una autoridad con la clave {clave}[/yellow]")
    elif autoridades.count() == 1:
        # Mostrar los detalles de una autoridad
        autoridad = autoridades.first()
        if autoridad is not None:
            console.print(f"[green]clave:[/green]                         {autoridad.clave}")
            console.print(f"[green]descripcion:[/green]                   {autoridad.descripcion}")
            console.print(f"[green]descripcion_corta:[/green]             {autoridad.descripcion_corta}")
            console.print(f"[green]estatus:[/green]                       {autoridad.estatus}")
            console.print(f"[green]directorio_edictos:[/green]            {autoridad.directorio_edictos}")
            console.print(f"[green]directorio_glosas:[/green]             {autoridad.directorio_glosas}")
            console.print(f"[green]directorio_listas_de_acuerdos:[/green] {autoridad.directorio_listas_de_acuerdos}")
            console.print(f"[green]directorio_sentencias:[/green]         {autoridad.directorio_sentencias}")
    else:
        # Mostrar tabla con todas las autoridades que coinciden con la clave
        tabla = Table(title="Autoridades")
        tabla.add_column("Clave", header_style="green", no_wrap=True)
        tabla.add_column("Descripción", header_style="green")
        tabla.add_column("Descripción corta", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        for autoridad in autoridades.all():
            tabla.add_row(autoridad.clave, autoridad.descripcion, autoridad.descripcion_corta, autoridad.estatus)
        console.print(tabla)
