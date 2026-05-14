"""
Fin Vales
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class FinVale(Base):
    """FinVale"""

    ESTADOS = {
        "CREADO": "Creado",  # PASO 1 Un usuario lo ha creado
        "SOLICITADO": "Solicitado",  # PASO 2 El solicitante lo ha firmado
        "CANCELADO POR SOLICITANTE": "Cancelado por solicitante",  # El solicitante lo ha cancelado
        "AUTORIZADO": "Autorizado",  # PASO 3 El autorizante lo ha firmado
        "CANCELADO POR AUTORIZANTE": "Cancelado por autorizante",  # El autorizante lo ha cancelado
        "ENTREGADO": "Entregado",  # PASO 4 El vale ha sido entregado
        "POR REVISAR": "Por revisar",  # PASO 5 Se han subido los archivos como evidencia
        "ARCHIVADO": "Archivado",  # PASO 6 Se ha archivado
    }

    TIPOS = {
        "NO DEFINIDO": "No definido",
        "GASOLINA": "Gasolina",
    }

    # Nombre de la tabla
    __tablename__ = "fin_vales"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="fin_vales")

    # Columnas CREADO: PASO 1 Un usuario lo ha creado
    estado: Mapped[str] = mapped_column(Enum(*ESTADOS, name="fin_vales_estados", native_enum=False), index=True)
    tipo: Mapped[str] = mapped_column(Enum(*TIPOS, name="fin_vales_tipos", native_enum=False), index=True)
    justificacion: Mapped[str] = mapped_column(Text())
    monto: Mapped[float]

    # Columnas SOLICITADO: PASO 2 El solicitante lo ha firmado
    solicito_nombre: Mapped[Optional[str]] = mapped_column(String(256))
    solicito_puesto: Mapped[Optional[str]] = mapped_column(String(256))
    solicito_email: Mapped[Optional[str]] = mapped_column(String(256))
    solicito_efirma_tiempo: Mapped[Optional[datetime]]
    solicito_efirma_folio: Mapped[Optional[int]]
    solicito_efirma_sello_digital: Mapped[Optional[str]] = mapped_column(String(256))
    solicito_efirma_url: Mapped[Optional[str]] = mapped_column(String(256))
    solicito_efirma_qr_url: Mapped[Optional[str]] = mapped_column(String(256))
    solicito_efirma_mensaje: Mapped[Optional[str]] = mapped_column(String(512))
    solicito_efirma_error: Mapped[Optional[str]] = mapped_column(String(512))

    # Columnas CANCELADO POR SOLICITANTE: El solicitante lo ha cancelado
    solicito_cancelo_tiempo: Mapped[Optional[datetime]]
    solicito_cancelo_motivo: Mapped[Optional[str]] = mapped_column(String(256))
    solicito_cancelo_error: Mapped[Optional[str]] = mapped_column(String(512))

    # Columnas AUTORIZADO: PASO 3 El autorizante lo ha firmado
    autorizo_nombre: Mapped[Optional[str]] = mapped_column(String(256))
    autorizo_puesto: Mapped[Optional[str]] = mapped_column(String(256))
    autorizo_email: Mapped[Optional[str]] = mapped_column(String(256))
    autorizo_efirma_tiempo: Mapped[Optional[datetime]]
    autorizo_efirma_folio: Mapped[Optional[int]]
    autorizo_efirma_sello_digital: Mapped[Optional[str]] = mapped_column(String(256))
    autorizo_efirma_url: Mapped[Optional[str]] = mapped_column(String(256))
    autorizo_efirma_qr_url: Mapped[Optional[str]] = mapped_column(String(256))
    autorizo_efirma_mensaje: Mapped[Optional[str]] = mapped_column(String(512))
    autorizo_efirma_error: Mapped[Optional[str]] = mapped_column(String(512))

    # Columnas CANCELADO POR AUTORIZANTE: El autorizante lo ha cancelado
    autorizo_cancelo_tiempo: Mapped[Optional[datetime]]
    autorizo_cancelo_motivo: Mapped[Optional[str]] = mapped_column(String(256))
    autorizo_cancelo_error: Mapped[Optional[str]] = mapped_column(String(512))

    # Columnas ENTREGADO: PASO 4 El vale ha sido entregado
    folio: Mapped[Optional[int]]

    # Columnas POR REVISAR: PASO 5 Se han subido los archivos como evidencia
    vehiculo_descripcion: Mapped[Optional[str]] = mapped_column(String(256))
    tanque_inicial: Mapped[Optional[str]] = mapped_column(String(48))
    tanque_final: Mapped[Optional[str]] = mapped_column(String(48))
    kilometraje_inicial: Mapped[Optional[int]]
    kilometraje_final: Mapped[Optional[int]]

    # Columnas ARCHIVADO: PASO 6 Se ha archivado
    notas: Mapped[Optional[str]] = mapped_column(String(1024))

    def __repr__(self):
        """Representación"""
        return f"<FinVale {self.id}>"
