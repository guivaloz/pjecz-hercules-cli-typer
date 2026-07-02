"""
Autoridades
"""

from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class Autoridad(Base):
    """Autoridad"""

    # Nombre de la tabla
    __tablename__ = "autoridades"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    distrito_id: Mapped[int] = mapped_column(ForeignKey("distritos.id"))
    distrito: Mapped["Distrito"] = relationship(back_populates="autoridades")
    materia_id: Mapped[int] = mapped_column(ForeignKey("materias.id"))
    materia: Mapped["Materia"] = relationship(back_populates="autoridades")

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    descripcion: Mapped[str] = mapped_column(String(256))
    descripcion_corta: Mapped[str] = mapped_column(String(64))
    directorio_edictos: Mapped[str] = mapped_column(String(256))
    directorio_estrados: Mapped[str] = mapped_column(String(256))
    directorio_glosas: Mapped[str] = mapped_column(String(256))
    directorio_listas_de_acuerdos: Mapped[str] = mapped_column(String(256))
    directorio_sentencias: Mapped[str] = mapped_column(String(256))
    es_archivo_solicitante: Mapped[bool] = mapped_column(default=False)
    es_cemasc: Mapped[bool] = mapped_column(default=False)
    es_defensoria: Mapped[bool] = mapped_column(default=False)
    es_extinto: Mapped[bool] = mapped_column(default=False)
    es_jurisdiccional: Mapped[bool] = mapped_column(default=False)
    es_notaria: Mapped[bool] = mapped_column(default=False)
    es_organo_especializado: Mapped[bool] = mapped_column(default=False)
    es_revisor_escrituras: Mapped[bool] = mapped_column(default=False)
    es_vsp_digitalizaciones: Mapped[bool] = mapped_column(default=False)
    pagina_cabecera_url: Mapped[Optional[str]]
    pagina_pie_url: Mapped[Optional[str]]
    tabla_renglon_color: Mapped[Optional[str]]
    tablero_icono: Mapped[Optional[str]]
    destinatarios_emails: Mapped[Optional[str]] = mapped_column(String(1024))
    con_copias_emails: Mapped[Optional[str]] = mapped_column(String(1024))

    # Hijos
    edictos: Mapped[List["Edicto"]] = relationship("Edicto", back_populates="autoridad")
    listas_de_acuerdos: Mapped[List["ListaDeAcuerdo"]] = relationship("ListaDeAcuerdo", back_populates="autoridad")
    sentencias: Mapped[List["Sentencia"]] = relationship("Sentencia", back_populates="autoridad")
    usuarios: Mapped[List["Usuario"]] = relationship("Usuario", back_populates="autoridad")
    vsp_digitalizaciones: Mapped[List["VspDigitalizacion"]] = relationship(back_populates="autoridad")

    def __repr__(self):
        """Representación"""
        return f"<Autoridad {self.clave}>"
