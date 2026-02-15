"""
PJECZ Hercules CLI Typer App

Interfaz de linea de comandos hecha con Typer y Python para Plataforma Web.
"""

from typer import Typer

from .commands.autoridades.app import app as autoridades_app
from .commands.distritos.app import app as distritos_app
from .commands.materias.app import app as materias_app

app = Typer()
app.add_typer(autoridades_app, name="autoridades")
app.add_typer(distritos_app, name="distritos")
app.add_typer(materias_app, name="materias")

if __name__ == "__main__":
    app()
