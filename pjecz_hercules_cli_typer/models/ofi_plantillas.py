"""
Oficios Plantillas
"""

from datetime import datetime, date
from typing import Optional
import uuid

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..utils.database import Base


class OfiPlantilla(Base):
    """OfiPlantilla"""

    # Nombre de la tabla
    __tablename__ = "ofi_plantillas"

    # Clave primaria
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Clave foránea
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="ofi_plantillas")

    # Columnas
    descripcion: Mapped[str] = mapped_column(String(256))
    destinatarios_emails: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    con_copias_emails: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    remitente_email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    esta_archivado: Mapped[bool] = mapped_column(default=False)
    esta_compartida: Mapped[bool] = mapped_column(default=False)

    # Columnas contenido
    contenido_html: Mapped[Optional[str]] = mapped_column(Text)
    contenido_md: Mapped[Optional[str]] = mapped_column(Text)
    contenido_sfdt: Mapped[Optional[JSONB]] = mapped_column(JSONB)

    def __repr__(self):
        """Representación"""
        return f"<OfiPlantilla {self.id}>"
