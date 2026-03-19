"""
Autoridades command
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Typer

from ..models.autoridades import Autoridad
from ..utils.database import get_database
from ..utils.safe_string import safe_clave

app = Typer(help="Autoridades")


@app.command()
def query(clave: str = "", offset: int = 0, limit: int = 10):
    """Consultar autoridades"""
    console = Console()
    console.print("Consultando autoridades...")

    # Consultar
    db = get_database()

    # Si viene la clave
    if clave != "":
        # Consultar una autoridad específica
        clave = safe_clave(clave)
        if clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        stmt = (
            select(
                Autoridad.clave,
                Autoridad.descripcion,
                Autoridad.descripcion_corta,
                Autoridad.directorio_edictos,
                Autoridad.directorio_glosas,
                Autoridad.directorio_listas_de_acuerdos,
                Autoridad.directorio_sentencias,
                Autoridad.estatus,
            ).where(Autoridad.clave == clave)
        )
        autoridad = db.execute(stmt).first()
        if autoridad is not None:
            # Mostrar detalle de una autoridad y salir
            console.print(f"[green]clave:[/green]                         {autoridad.clave}")
            console.print(f"[green]descripcion:[/green]                   {autoridad.descripcion}")
            console.print(f"[green]descripcion_corta:[/green]             {autoridad.descripcion_corta}")
            console.print(f"[green]directorio_edictos:[/green]            {autoridad.directorio_edictos}")
            console.print(f"[green]directorio_glosas:[/green]             {autoridad.directorio_glosas}")
            console.print(f"[green]directorio_listas_de_acuerdos:[/green] {autoridad.directorio_listas_de_acuerdos}")
            console.print(f"[green]directorio_sentencias:[/green]         {autoridad.directorio_sentencias}")
            console.print(f"[green]estatus:[/green]                       {autoridad.estatus}")
            return Exit(code=0)

    # De lo contrario, mostrar tabla con autoridades
    stmt = (
        select(
            Autoridad.clave,
            Autoridad.descripcion,
            Autoridad.descripcion_corta,
            Autoridad.estatus,
        )
    )
    if clave != "":
        stmt = stmt.where(Autoridad.clave.contains(clave))
    stmt = stmt.order_by(Autoridad.clave).offset(offset).limit(limit)
    tabla = Table(title="Autoridades")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")
    tabla.add_column("Descripción corta", header_style="green")
    tabla.add_column("Estatus", header_style="green")
    for item in db.execute(stmt):
        tabla.add_row(item.clave, item.descripcion, item.descripcion_corta, item.estatus)
    console.print(tabla)
