"""
Usuarios
"""

from typing import List, Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..utils.database import Base


class Usuario(Base):
    """Usuario"""

    WORKSPACES = {
        "BUSINESS STARTED": "Business Started",
        "BUSINESS STANDARD": "Business Standard",
        "COAHUILA": "Coahuila",
        "EXTERNO": "Externo",
    }

    # Nombre de la tabla
    __tablename__ = "usuarios"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Claves foráneas
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="usuarios")

    # Columnas
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    nombres: Mapped[str] = mapped_column(String(256))
    apellido_paterno: Mapped[str] = mapped_column(String(256))
    apellido_materno: Mapped[str] = mapped_column(String(256))
    curp: Mapped[str] = mapped_column(String(18), default="")
    puesto: Mapped[str] = mapped_column(String(256), default="")
    efirma_registro_id: Mapped[Optional[int]]
    workspace: Mapped[str] = mapped_column(Enum(*WORKSPACES, name="usuarios_workspaces", native_enum=False), index=True)

    # Hijos
    fin_vales: Mapped[List["FinVale"]] = relationship("FinVale", back_populates="usuario")
    inv_custodias: Mapped[List["InvCustodia"]] = relationship("InvCustodia", back_populates="usuario")
    ofi_documentos: Mapped[List["OfiDocumento"]] = relationship("OfiDocumento", back_populates="usuario")
    ofi_plantillas: Mapped[List["OfiPlantilla"]] = relationship("OfiPlantilla", back_populates="usuario")
    soportes_tickets: Mapped[List["SoporteTicket"]] = relationship("SoporteTicket", back_populates="usuario")
    usuarios_roles: Mapped[List["UsuarioRol"]] = relationship("UsuarioRol", back_populates="usuario")

    @property
    def nombre(self):
        """Junta nombres, apellido primero y apellido segundo"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

    @property
    def siglas(self):
        """Genera siglas a partir de los nombres y apellidos"""
        siglas = ""
        if self.nombres:
            nombres_palabras = self.nombres.split()
            for palabra in nombres_palabras:
                siglas += palabra[0].upper()
        if self.apellido_paterno:
            apellido_paterno_palabras = self.apellido_paterno.split()
            for palabra in apellido_paterno_palabras:
                siglas += palabra[0].upper()
        if self.apellido_materno:
            apellido_materno_palabras = self.apellido_materno.split()
            for palabra in apellido_materno_palabras:
                siglas += palabra[0].upper()
        return siglas

    def __repr__(self):
        """Representación"""
        return f"<Usuario {self.email}>"
