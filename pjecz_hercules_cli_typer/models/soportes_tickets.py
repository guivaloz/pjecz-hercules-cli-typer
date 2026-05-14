"""
Soportes Tickets
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class SoporteTicket(Base):
    """SoporteTicket"""

    ESTADOS = {
        "SIN ATENDER": "Abierto o pendiente",
        "TRABAJANDO": "Trabajando",
        "TERMINADO": "Trabajo concluido, resultado satisfactorio",
        "CERRADO": "Trabajo concluido, resultado indiferente",
        "PENDIENTE": "Pendiente de resolver",
        "CANCELADO": "Cancelado",
    }

    CLASIFICACIONES = {
        "INFRAESTRUCTURA": "INFRAESTRUCTURA",
        "PAIIJ": "PAIIJ",
        "SIGE": "SIGE",
        "SAJI HIPOTECARIO": "SAJI HIPOTECARIO",
        "SAJI LABORAL": "SAJI LABORAL",
        "SICCED": "SICCED",
        "SOPORTE TECNICO": "SOPORTE TÉCNICO",
        "OTRO": "OTRO",
    }

    DEPARTAMENTOS = {
        "INFORMATICA": "INFORMATICA",
        "INFRAESTRUCTURA": "INFRAESTRUCTURA",
    }

    # Nombre de la tabla
    __tablename__ = "soportes_tickets"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    # funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionarios.id"))
    # funcionario: Mapped["Funcionario"] = relationship(back_populates="soportes_tickets")
    # soporte_categoria_id: Mapped[int] = mapped_column(ForeignKey("soportes_categorias.id"))
    # soporte_categoria: Mapped["SoporteCategoria"] = relationship(back_populates="soportes_tickets")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="soportes_tickets")

    # Columnas
    descripcion: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="soportes_tickets_estados", native_enum=False), index=True)
    resolucion: Mapped[Optional[datetime]] = mapped_column(DateTime)
    soluciones: Mapped[Optional[str]] = mapped_column(Text)
    departamento: Mapped[str] = mapped_column(
        Enum(*DEPARTAMENTOS, name="soportes_tickets_departamentos", native_enum=False), index=True
    )

    def __repr__(self):
        """Representación"""
        return f"<SoporteTicket {self.id}>"
