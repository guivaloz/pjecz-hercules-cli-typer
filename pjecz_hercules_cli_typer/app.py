"""
PJECZ Hercules CLI Typer App

Interfaz de linea de comandos hecha con Typer y Python para Plataforma Web.
"""

from typer import Typer

from pjecz_hercules_cli_typer.commands.autoridades import app as autoridades_app
from pjecz_hercules_cli_typer.commands.distritos import app as distritos_app
from pjecz_hercules_cli_typer.commands.edictos import app as edictos_app
from pjecz_hercules_cli_typer.commands.materias import app as materias_app
from pjecz_hercules_cli_typer.commands.ofi_plantillas import app as ofi_plantillas_app
from pjecz_hercules_cli_typer.commands.usuarios_roles import app as usuarios_roles_app
from pjecz_hercules_cli_typer.commands.vsp_digitalizaciones import app as vsp_digitalizaciones_app

app = Typer()
app.add_typer(autoridades_app, name="autoridades")
app.add_typer(distritos_app, name="distritos")
app.add_typer(edictos_app, name="edictos")
app.add_typer(materias_app, name="materias")
app.add_typer(ofi_plantillas_app, name="ofi-plantillas")
app.add_typer(usuarios_roles_app, name="usuarios-roles")
app.add_typer(vsp_digitalizaciones_app, name="vsp-digitalizaciones")

if __name__ == "__main__":
    app()
