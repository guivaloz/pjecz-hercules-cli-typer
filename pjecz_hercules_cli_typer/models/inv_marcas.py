"""
Inv Marcas
"""

from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..utils.database import Base


class InvMarca(Base):

    # Nombre de la tabla
    __tablename__ = "inv_marcas"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256))

    # Hijos
    inv_modelos: Mapped[List["InvModelo"]] = relationship(back_populates="inv_marca")

    def __repr__(self):
        """Representación"""
        return f"<InvMarca {self.id}>"
