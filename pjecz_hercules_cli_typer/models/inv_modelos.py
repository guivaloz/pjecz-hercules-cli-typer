"""
Inv Modelos
"""

from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class InvModelo(Base):
    # Nombre de la tabla
    __tablename__ = "inv_modelos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    inv_marca_id: Mapped[int] = mapped_column(ForeignKey("inv_marcas.id"))
    inv_marca: Mapped["InvMarca"] = relationship(back_populates="inv_modelos")

    # Columnas
    descripcion: Mapped[str] = mapped_column(String(256))

    # Hijos
    inv_equipos: Mapped[List["InvEquipo"]] = relationship(back_populates="inv_modelo")

    def __repr__(self):
        """Representación"""
        return f"<InvModelo {self.id}>"
