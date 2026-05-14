"""
Distritos command
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Typer

from pjecz_hercules_cli_typer.models.distritos import Distrito
from pjecz_hercules_cli_typer.utils.database import get_database
from pjecz_hercules_cli_typer.utils.safe_string import safe_clave

app = Typer(help="Distritos")


@app.command()
def query(clave: str = "", offset: int = 0, limit: int = 10):
    """Consultar distritos"""
    console = Console()
    console.print("Consultando distritos...")

    # Consultar
    db = get_database()

    # Si viene la clave
    if clave != "":
        # Consultar un distrito específico
        clave = safe_clave(clave)
        if clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        stmt = select(
            Distrito.clave,
            Distrito.nombre,
            Distrito.nombre_corto,
            Distrito.estatus,
        ).where(Distrito.clave == clave)
        distrito = db.execute(stmt).first()
        if distrito is None:
            console.print(f"[yellow]No se encontró una distrito con la clave {clave}[/yellow]")
            raise Exit(code=1)
        console.print(f"[green]clave:[/green]        {distrito.clave}")
        console.print(f"[green]nombre:[/green]       {distrito.nombre}")
        console.print(f"[green]nombre_corto:[/green] {distrito.nombre_corto}")
        console.print(f"[green]estatus:[/green]      {distrito.estatus}")
        return Exit(code=0)

    # De lo contrario, consultar todas los distritos
    stmt = (
        select(
            Distrito.clave,
            Distrito.nombre,
            Distrito.nombre_corto,
            Distrito.estatus,
        )
        .order_by(Distrito.clave)
        .offset(offset)
        .limit(limit)
    )
    tabla = Table(title="Distritos")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Nombre", header_style="green")
    tabla.add_column("Nombre corto", header_style="green")
    tabla.add_column("Estatus", header_style="green")
    for item in db.execute(stmt):
        tabla.add_row(item.clave, item.nombre, item.nombre_corto, item.estatus)
    console.print(tabla)
