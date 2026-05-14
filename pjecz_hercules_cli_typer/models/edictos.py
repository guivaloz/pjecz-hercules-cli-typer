"""
Edictos
"""

from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class Edicto(Base):
    """Edicto"""

    # Nombre de la tabla
    __tablename__ = "edictos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="edictos")

    # Columnas
    fecha: Mapped[date] = mapped_column(index=True)
    descripcion: Mapped[str] = mapped_column(String(256))
    expediente: Mapped[str] = mapped_column(String(16))
    numero_publicacion: Mapped[str] = mapped_column(String(16))
    archivo: Mapped[str] = mapped_column(String(256), default="")
    url: Mapped[str] = mapped_column(String(512), default="")
    acuse_num: Mapped[int] = mapped_column(default=0)
    edicto_id_original: Mapped[int] = mapped_column(default=0)
    es_declaracion_de_ausencia: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        """Representación"""
        return f"<Edicto {self.id}>"
