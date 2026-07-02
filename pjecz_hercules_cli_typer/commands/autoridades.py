"""
Autoridades command
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Typer

from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.utils.database import get_database
from pjecz_hercules_cli_typer.utils.safe_string import safe_clave

app = Typer(help="Autoridades")


@app.command()
def consultar(clave: str = "", offset: int = 0, limit: int = 100):
    """Consultar autoridades"""
    console = Console()
    console.print("Consultando autoridades...")

    # Inicializar la base de datos
    db = get_database()

    # Si viene la clave
    if clave != "":
        # Consultar una autoridad específica
        clave = safe_clave(clave)
        if clave == "":
            console.print("[red]Clave inválida[/red]")
            raise Exit(code=1)
        stmt = select(
            Autoridad.clave,
            Autoridad.descripcion,
            Autoridad.descripcion_corta,
            Autoridad.directorio_edictos,
            Autoridad.directorio_estrados,
            Autoridad.directorio_glosas,
            Autoridad.directorio_listas_de_acuerdos,
            Autoridad.directorio_sentencias,
            Autoridad.pagina_cabecera_url,
            Autoridad.pagina_pie_url,
            Autoridad.tabla_renglon_color,
            Autoridad.tablero_icono,
            Autoridad.destinatarios_emails,
            Autoridad.con_copias_emails,
            Autoridad.estatus,
        ).where(Autoridad.clave == clave)
        autoridad = db.execute(stmt).first()
        if autoridad is None:
            console.print(f"[yellow]No se encontró una autoridad con la clave {clave}[/yellow]")
            raise Exit(code=1)
        console.print(f"[green]clave:[/green]                         {autoridad.clave}")
        console.print(f"[green]descripcion:[/green]                   {autoridad.descripcion}")
        console.print(f"[green]descripcion_corta:[/green]             {autoridad.descripcion_corta}")
        console.print(f"[green]directorio_edictos:[/green]            {autoridad.directorio_edictos}")
        console.print(f"[green]directorio_estrados:[/green]           {autoridad.directorio_estrados}")
        console.print(f"[green]directorio_glosas:[/green]             {autoridad.directorio_glosas}")
        console.print(f"[green]directorio_listas_de_acuerdos:[/green] {autoridad.directorio_listas_de_acuerdos}")
        console.print(f"[green]directorio_sentencias:[/green]         {autoridad.directorio_sentencias}")
        console.print(f"[green]pagina_cabecera_url:[/green]           {autoridad.pagina_cabecera_url}")
        console.print(f"[green]pagina_pie_url:[/green]                {autoridad.pagina_pie_url}")
        console.print(f"[green]tabla_renglon_color:[/green]           {autoridad.tabla_renglon_color}")
        console.print(f"[green]tablero_icono:[/green]                 {autoridad.tablero_icono}")
        console.print(f"[green]destinatarios_emails:[/green]          {autoridad.destinatarios_emails}")
        console.print(f"[green]con_copias_emails:[/green]             {autoridad.con_copias_emails}")
        console.print(f"[green]estatus:[/green]                       {autoridad.estatus}")
        return Exit(code=0)

    # De lo contrario, mostrar tabla con autoridades
    stmt = select(
        Autoridad.clave,
        Autoridad.descripcion,
        Autoridad.descripcion_corta,
        Autoridad.estatus,
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
