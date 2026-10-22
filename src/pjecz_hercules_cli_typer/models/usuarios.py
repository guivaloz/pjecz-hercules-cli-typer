"""
Usuarios
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.core.database import Base


class Usuario(Base):
    """Usuario"""

    # Nombre de la tabla
    __tablename__ = "usuarios"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="usuarios")
    oficina_id: Mapped[int] = mapped_column(ForeignKey("oficinas.id"))
    oficina: Mapped["Oficina"] = relationship(back_populates="usuarios")

    # Columnas
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    email_personal: Mapped[str] = mapped_column(String(256))
    nombres: Mapped[str] = mapped_column(String(256))
    apellido_paterno: Mapped[str] = mapped_column(String(256))
    apellido_materno: Mapped[str] = mapped_column(String(256))
    curp: Mapped[str] = mapped_column(String(18))
    puesto: Mapped[str] = mapped_column(String(256))
    titulo: Mapped[Optional[str]] = mapped_column(String(32))
    api_key: Mapped[Optional[str]] = mapped_column(String(128))
    api_key_expiracion: Mapped[Optional[datetime]]
    api_key_cuota_diaria: Mapped[Optional[int]]
    contrasena: Mapped[Optional[str]] = mapped_column(String(256))

    # Hijos
    arc_remesas: Mapped[list["ArcRemesa"]] = relationship(back_populates="usuario_asignado")
    bitacoras_apis: Mapped[list["BitacoraAPI"]] = relationship(back_populates="usuario")
    ofi_documentos: Mapped[list["OfiDocumento"]] = relationship(back_populates="usuario")
    ofi_documentos_destinatarios: Mapped[list["OfiDocumentoDestinatario"]] = relationship(back_populates="usuario")
    soportes_tickets: Mapped[list["SoporteTicket"]] = relationship(back_populates="usuario")
    usuarios_roles: Mapped[list["UsuarioRol"]] = relationship(back_populates="usuario")

    # Propiedades
    permisos_consultados = {}

    @property
    def nombre(self):
        """Junta nombres, apellido_paterno y apellido materno"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

    def __repr__(self):
        """Representación"""
        return f"<Usuario {self.email}>"
