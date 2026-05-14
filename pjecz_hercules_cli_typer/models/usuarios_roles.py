"""
Usuarios-Roles
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pjecz_hercules_cli_typer.utils.database import Base


class UsuarioRol(Base):
    """UsuarioRol"""

    # Nombre de la tabla
    __tablename__ = "usuarios_roles"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    rol: Mapped["Rol"] = relationship(back_populates="usuarios_roles")
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    usuario: Mapped["Usuario"] = relationship(back_populates="usuarios_roles")

    # Columnas
    descripcion: Mapped[str] = mapped_column(String(256))

    def __repr__(self):
        """Representación"""
        return f"<UsuarioRol {self.id}>"
