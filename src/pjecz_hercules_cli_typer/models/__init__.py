"""
Models

Importa todos los modelos para que SQLAlchemy pueda resolver las relaciones declaradas con nombres de clase.
"""

from pjecz_hercules_cli_typer.models.arc_documentos import ArcDocumento
from pjecz_hercules_cli_typer.models.arc_documentos_tipos import ArcDocumentoTipo
from pjecz_hercules_cli_typer.models.arc_juzgados_extintos import ArcJuzgadoExtinto
from pjecz_hercules_cli_typer.models.arc_remesas import ArcRemesa
from pjecz_hercules_cli_typer.models.arc_remesas_documentos import ArcRemesaDocumento
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.bitacoras_apis import BitacoraAPI
from pjecz_hercules_cli_typer.models.dgt_depositos import DgtDepositos
from pjecz_hercules_cli_typer.models.dgt_digitalizaciones import DgtDigitalizacion
from pjecz_hercules_cli_typer.models.dgt_entregas import DgtEntrega
from pjecz_hercules_cli_typer.models.dgt_plataformas import DgtPlataforma
from pjecz_hercules_cli_typer.models.dgt_plataformas_autoridades import DgtPlataformaAutoridad
from pjecz_hercules_cli_typer.models.dgt_plataformas_endpoints import DgtPlataformaEndpoint
from pjecz_hercules_cli_typer.models.dgt_rutas import DgtRuta
from pjecz_hercules_cli_typer.models.dgt_tipos import DgtTipo
from pjecz_hercules_cli_typer.models.distritos import Distrito
from pjecz_hercules_cli_typer.models.domicilios import Domicilio
from pjecz_hercules_cli_typer.models.edictos import Edicto
from pjecz_hercules_cli_typer.models.estados import Estado
from pjecz_hercules_cli_typer.models.exh_areas import ExhArea
from pjecz_hercules_cli_typer.models.exh_exhortos import ExhExhorto
from pjecz_hercules_cli_typer.models.exh_exhortos_archivos import ExhExhortoArchivo
from pjecz_hercules_cli_typer.models.exh_exhortos_partes import ExhExhortoParte
from pjecz_hercules_cli_typer.models.exh_tipos_diligencias import ExhTipoDiligencia
from pjecz_hercules_cli_typer.models.funcionarios import Funcionario
from pjecz_hercules_cli_typer.models.funcionarios_oficinas import FuncionarioOficina
from pjecz_hercules_cli_typer.models.glosas import Glosa
from pjecz_hercules_cli_typer.models.listas_de_acuerdos import ListaDeAcuerdo
from pjecz_hercules_cli_typer.models.materias import Materia
from pjecz_hercules_cli_typer.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_cli_typer.models.modulos import Modulo
from pjecz_hercules_cli_typer.models.municipios import Municipio
from pjecz_hercules_cli_typer.models.ofi_documentos import OfiDocumento
from pjecz_hercules_cli_typer.models.ofi_documentos_adjuntos import OfiDocumentoAdjunto
from pjecz_hercules_cli_typer.models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from pjecz_hercules_cli_typer.models.oficinas import Oficina
from pjecz_hercules_cli_typer.models.permisos import Permiso
from pjecz_hercules_cli_typer.models.redams import Redam
from pjecz_hercules_cli_typer.models.repsvm_agresores import RepsvmAgresor
from pjecz_hercules_cli_typer.models.roles import Rol
from pjecz_hercules_cli_typer.models.sentencias import Sentencia
from pjecz_hercules_cli_typer.models.soportes_categorias import SoporteCategoria
from pjecz_hercules_cli_typer.models.soportes_tickets import SoporteTicket
from pjecz_hercules_cli_typer.models.usuarios import Usuario
from pjecz_hercules_cli_typer.models.usuarios_roles import UsuarioRol

__all__ = [
    "ArcDocumento",
    "ArcDocumentoTipo",
    "ArcJuzgadoExtinto",
    "ArcRemesa",
    "ArcRemesaDocumento",
    "Autoridad",
    "BitacoraAPI",
    "DgtDepositos",
    "DgtDigitalizacion",
    "DgtEntrega",
    "DgtPlataforma",
    "DgtPlataformaAutoridad",
    "DgtPlataformaEndpoint",
    "DgtRuta",
    "DgtTipo",
    "Distrito",
    "Domicilio",
    "Edicto",
    "Estado",
    "ExhArea",
    "ExhExhorto",
    "ExhExhortoArchivo",
    "ExhExhortoParte",
    "ExhTipoDiligencia",
    "Funcionario",
    "FuncionarioOficina",
    "Glosa",
    "ListaDeAcuerdo",
    "Materia",
    "MateriaTipoJuicio",
    "Modulo",
    "Municipio",
    "OfiDocumento",
    "OfiDocumentoAdjunto",
    "OfiDocumentoDestinatario",
    "Oficina",
    "Permiso",
    "Redam",
    "RepsvmAgresor",
    "Rol",
    "Sentencia",
    "SoporteCategoria",
    "SoporteTicket",
    "Usuario",
    "UsuarioRol",
]
