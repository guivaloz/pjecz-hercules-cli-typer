"""
Edictos command
"""

from typer import Typer
from rich.console import Console
from rich.table import Table

from ...models.autoridades import Autoridad
from ...models.edictos import Edicto
from ...utils.database import get_database
from ...utils.safe_string import safe_clave

app = Typer(help="Edictos")


@app.command()
def query(edicto_id: int = 0, autoridad_clave: str = "", limit: int = 10):
    """Consultar edictos"""
    console = Console()
    console.print("Consultando edictos...")

    # Consultar
    db = get_database()

    # Si se especificó un ID, consultar un edicto
    if edicto_id:
        edicto = db.query(Edicto).get(edicto_id)
        if edicto:
            console.print(f"ID: {edicto.id}")
            console.print(f"Autoridad: {edicto.autoridad.clave}")
            console.print(f"Expediente: {edicto.expediente}")
            console.print(f"Descripción: {edicto.descripcion}")
            console.print(f"Estatus: {edicto.estatus}")
        else:
            console.print(f"No se encontró el edicto con ID {edicto_id}")
        return

    # Si se especificó una clave de autoridad, consultar los edictos de esa autoridad
    if autoridad_clave:
        autoridad_clave = safe_clave(autoridad_clave)
        if autoridad_clave == "":
            console.print("[red]Clave inválida[/red]")
            return
        edictos = db.query(Edicto).join(Autoridad).filter(Autoridad.clave == autoridad_clave).order_by(Edicto.id.desc()).limit(limit)
        if edictos.count() == 0:
            console.print(f"[yellow]No se encontraron edictos para la autoridad {autoridad_clave}[/yellow]")
        else:
            tabla = Table(title=f"Edictos de la autoridad {autoridad_clave}")
            tabla.add_column("ID", header_style="green", no_wrap=True)
            tabla.add_column("Autoridad", header_style="green")
            tabla.add_column("Expediente", header_style="green")
            tabla.add_column("Descripción", header_style="green")
            tabla.add_column("Estatus", header_style="green")
            for edicto in edictos.limit(limit).all():
                tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.expediente, edicto.descripcion, edicto.estatus)
            console.print(tabla)
        return

    # Consultar los edictos más recientes
    edictos = db.query(Edicto).order_by(Edicto.id.desc()).limit(limit)
    if edictos.count() == 0:
        console.print("[yellow]No se encontraron edictos[/yellow]")
    else:
        tabla = Table(title="Edictos más recientes")
        tabla.add_column("ID", header_style="green", no_wrap=True)
        tabla.add_column("Autoridad", header_style="green")
        tabla.add_column("Expediente", header_style="green")
        tabla.add_column("Descripción", header_style="green")
        tabla.add_column("Estatus", header_style="green")
        for edicto in edictos.all():
            tabla.add_row(str(edicto.id), edicto.autoridad.clave, edicto.expediente, edicto.descripcion, edicto.estatus)
        console.print(tabla)
