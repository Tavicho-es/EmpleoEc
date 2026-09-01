from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base



# USUARIOS


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    tipo_usuario = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())

    candidato = relationship(
        "Candidato",
        back_populates="usuario",
        uselist=False
    )

    empresa = relationship(
        "Empresa",
        back_populates="usuario",
        uselist=False
    )

# CANDIDATOS


class Candidato(Base):
    __tablename__ = "candidatos"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    telefono = Column(String(30))
    ciudad = Column(String(100))
    provincia = Column(String(100))
    profesion = Column(String(150))
    descripcion = Column(Text)
    cv_url = Column(String(500))

    fecha_creacion = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="candidato"
    )

    postulaciones = relationship(
        "Postulacion",
        back_populates="candidato",
        cascade="all, delete-orphan"
    )



# EMPRESAS


class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    nombre_empresa = Column(String(200), nullable=False)
    descripcion = Column(Text)
    telefono = Column(String(30))
    ciudad = Column(String(100))
    provincia = Column(String(100))
    direccion = Column(String(250))
    sitio_web = Column(String(300))

    fecha_creacion = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="empresa"
    )

    ofertas = relationship(
        "OfertaEmpleo",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )



# OFERTAS DE EMPLEO


class OfertaEmpleo(Base):
    __tablename__ = "ofertas_empleo"

    id = Column(Integer, primary_key=True, index=True)

    empresa_id = Column(
        Integer,
        ForeignKey("empresas.id", ondelete="CASCADE"),
        nullable=False
    )

    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    requisitos = Column(Text)

    ubicacion = Column(String(200))
    tipo_empleo = Column(String(50))

    salario_minimo = Column(Numeric(10, 2))
    salario_maximo = Column(Numeric(10, 2))

    estado = Column(
        String(20),
        nullable=False,
        default="activa"
    )

    fecha_publicacion = Column(
        DateTime,
        server_default=func.now()
    )

    empresa = relationship(
        "Empresa",
        back_populates="ofertas"
    )

    postulaciones = relationship(
        "Postulacion",
        back_populates="oferta",
        cascade="all, delete-orphan"
    )



# POSTULACIONES


class Postulacion(Base):
    __tablename__ = "postulaciones"

    id = Column(Integer, primary_key=True, index=True)

    candidato_id = Column(
        Integer,
        ForeignKey("candidatos.id", ondelete="CASCADE"),
        nullable=False
    )

    oferta_id = Column(
        Integer,
        ForeignKey("ofertas_empleo.id", ondelete="CASCADE"),
        nullable=False
    )

    estado = Column(
        String(30),
        nullable=False,
        default="pendiente"
    )

    fecha_postulacion = Column(
        DateTime,
        server_default=func.now()
    )

    candidato = relationship(
        "Candidato",
        back_populates="postulaciones"
    )

    oferta = relationship(
        "OfertaEmpleo",
        back_populates="postulaciones"
    )