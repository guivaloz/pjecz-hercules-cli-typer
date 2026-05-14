"""
Roles
"""

from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class Rol(Base):
    """Rol"""

    # Nombre de la tabla
    __tablename__ = "roles"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Columnas
    nombre: Mapped[str] = mapped_column(String(256), unique=True)

    # Hijos
    usuarios_roles: Mapped[List["UsuarioRol"]] = relationship("UsuarioRol", back_populates="rol")

    def __repr__(self):
        """Representación"""
        return f"<Rol {self.nombre}>"
