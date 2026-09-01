from pydantic import BaseModel, EmailStr
from typing import Optional


# =========================
# USUARIO
# =========================

class UsuarioRegistro(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    tipo_usuario: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


# =========================
# PERFIL DEL CANDIDATO
# =========================

class CandidatoCrear(BaseModel):
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    profesion: Optional[str] = None
    descripcion: Optional[str] = None
    cv_url: Optional[str] = None


class CandidatoPerfil(BaseModel):
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    profesion: Optional[str] = None
    descripcion: Optional[str] = None
    cv_url: Optional[str] = None


class CandidatoRespuesta(BaseModel):
    id: int
    usuario_id: int
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    profesion: Optional[str] = None
    descripcion: Optional[str] = None
    cv_url: Optional[str] = None

    class Config:
        from_attributes = True

# =========================================================
# PERFIL DE EMPRESA
# =========================================================

class EmpresaCrear(BaseModel):
    nombre_empresa: str
    descripcion: Optional[str] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    direccion: Optional[str] = None
    sitio_web: Optional[str] = None


class EmpresaRespuesta(BaseModel):
    id: int
    usuario_id: int
    nombre_empresa: str
    descripcion: Optional[str] = None
    telefono: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    direccion: Optional[str] = None
    sitio_web: Optional[str] = None

    class Config:
        from_attributes = True