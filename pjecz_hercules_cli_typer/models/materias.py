"""
Materias
"""

from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class Materia(Base):
    """Materia"""

    # Nombre de la tabla
    __tablename__ = "materias"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    clave: Mapped[str] = mapped_column(String(16), unique=True)
    nombre: Mapped[str] = mapped_column(String(256), unique=True)
    descripcion: Mapped[str] = mapped_column(String(1024))
    en_sentencias: Mapped[bool] = mapped_column(default=False)

    # Hijos
    autoridades: Mapped[List["Autoridad"]] = relationship(back_populates="materia")
    materias_tipos_juicios: Mapped[List["MateriaTipoJuicio"]] = relationship(back_populates="materia")

    def __repr__(self):
        """Representación"""
        return f"<Materia {self.clave}>"
