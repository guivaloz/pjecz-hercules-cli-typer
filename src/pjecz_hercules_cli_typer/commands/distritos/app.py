"""
Distritos command
"""

from typer import Exit, Typer
from rich.console import Console
from rich.table import Table

from ...models.distritos import Distrito
from ...utils.database import get_database
from ...utils.safe_string import safe_clave

app = Typer(help="Distritos")


@app.command()
def query(clave: str = "", offset: int = 0, limit: int = 10):
    """Consultar distritos"""
    console = Console()
    console.print("Consultando distritos...")

    # Consultar
    db = get_database()

    # Si NO viene la clave, se van a mostrar todos los distritos
    if clave == "":
        tabla = Table(title="Distritos")
        tabla.add_column("Clave", header_style="green", no_wrap=True)
        tabla.add_column("Nombre", header_style="green")
        tabla.add_column("Nombre corto", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        for distrito in db.query(Distrito).order_by(Distrito.clave).offset(offset).limit(limit).all():
            tabla.add_row(distrito.clave, distrito.nombre, distrito.nombre_corto, distrito.estatus)
        console.print(tabla)
        return

    # Si viene la clave
    clave = safe_clave(clave)
    if clave == "":
        console.print("[red]Clave inválida[/red]")
        raise Exit(code=1)
    distritos = db.query(Distrito).filter(Distrito.clave.contains(clave)).order_by(Distrito.clave).offset(offset).limit(limit)
    if distritos.count() == 0:
        console.print(f"[yellow]No se encontró un distrito con la clave {clave}[/yellow]")
        raise Exit(code=1)
    elif distritos.count() == 1:
        # Mostrar los detalles de un distrito
        distrito = distritos.first()
        if distrito is not None:
            console.print(f"[green]clave:[/green]        {distrito.clave}")
            console.print(f"[green]nombre:[/green]       {distrito.nombre}")
            console.print(f"[green]nombre_corto:[/green] {distrito.nombre_corto}")
            console.print(f"[green]estatus:[/green]      {distrito.estatus}")
    else:
        # Mostrar tabla con todas los distritos que coinciden con la clave
        tabla = Table(title="Distritos")
        tabla.add_column("Clave", header_style="green", no_wrap=True)
        tabla.add_column("Nombre", header_style="green")
        tabla.add_column("Nombre corto", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        for distrito in db.query(Distrito).all():
            tabla.add_row(distrito.clave, distrito.nombre, distrito.nombre_corto, distrito.estatus)
        console.print(tabla)
