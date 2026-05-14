"""
Inv Equipos
"""

from datetime import date
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class InvEquipo(Base):
    ESTADOS = {
        "ALMACENADO": "ALMACENADO",
        "EN USO": "EN USO",
        "EN REPARACION": "EN REPARACION",
        "INSERVIBLE": "INSERVIBLE",
    }

    TIPOS = {
        "COMPUTADORA": "COMPUTADORA",
        "LAPTOP": "LAPTOP",
        "IMPRESORA": "IMPRESORA",
        "MULTIFUNCIONAL": "MULTIFUNCIONAL",
        "TELEFONIA": "TELEFONIA",
        "SERVIDOR": "SERVIDOR",
        "SCANNER": "SCANNER",
        "SWITCH": "SWITCH",
        "VIDEOGRABACION": "VIDEOGRABACION",
        "OTROS": "OTROS",
    }

    # Nombre de la tabla
    __tablename__ = "inv_equipos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    inv_custodia_id: Mapped[int] = mapped_column(ForeignKey("inv_custodias.id"))
    inv_custodia: Mapped["InvCustodia"] = relationship(back_populates="inv_equipos")
    inv_modelo_id: Mapped[int] = mapped_column(ForeignKey("inv_modelos.id"))
    inv_modelo: Mapped["InvModelo"] = relationship(back_populates="inv_equipos")

    # Columnas
    fecha_fabricacion: Mapped[Optional[date]]
    fecha_fabricacion_anio: Mapped[Optional[int]]
    numero_serie: Mapped[Optional[str]] = mapped_column(String(256))
    numero_inventario: Mapped[Optional[int]]
    descripcion: Mapped[str] = mapped_column(String(256))
    tipo: Mapped[str] = mapped_column(Enum(*TIPOS, name="inv_equipos_tipos", native_enum=False), index=True)
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="inv_equipos_estados", native_enum=False), index=True)

    def __repr__(self):
        """Representación"""
        return f"<InvEquipo {self.id}>"
