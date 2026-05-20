"""
Inv Custodias
"""

from datetime import date
from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class InvCustodia(Base):
    """InvCustodia"""

    # Nombre de la tabla
    __tablename__ = "inv_custodias"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="inv_custodias")

    # Columnas
    fecha: Mapped[date] = mapped_column(index=True)
    curp: Mapped[str] = mapped_column(String(256))
    nombre_completo: Mapped[str] = mapped_column(String(256))
    equipos_cantidad: Mapped[int]
    equipos_fotos_cantidad: Mapped[int]

    # Hijos
    inv_equipos: Mapped[List["InvEquipo"]] = relationship(back_populates="inv_custodia")

    def __repr__(self):
        """Representación"""
        return f"<InvCustodia {self.id}>"
