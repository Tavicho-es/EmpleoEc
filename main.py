from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from fastapi.responses import FileResponse

import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import models
import schemas

from database import engine, SessionLocal

from security import (
    crear_hash_password,
    verificar_password,
    crear_token_acceso,
    verificar_token
)

# =========================================================
# CREAR TABLAS
# =========================================================

models.Base.metadata.create_all(bind=engine)
# =========================================================
# CARPETA PARA GUARDAR CV
# =========================================================

CARPETA_CV = "uploads"

os.makedirs(CARPETA_CV, exist_ok=True)


# =========================================================
# CREAR APLICACIÓN
# =========================================================

app = FastAPI(
    title="EmpleaEC API",
    description="API de nuestra plataforma de empleo",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CONEXIÓN CON BASE DE DATOS
# =========================================================

def obtener_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# AUTENTICACIÓN JWT
# =========================================================

seguridad = HTTPBearer()


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(seguridad),
    db: Session = Depends(obtener_db)
):

    token = credenciales.credentials

    payload = verificar_token(token)

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )

    usuario_id = payload.get("sub")

    if usuario_id is None:

        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    try:

        usuario_id = int(usuario_id)

    except ValueError:

        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    usuario = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.id == usuario_id
        )
        .first()
    )

    if usuario is None:

        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    return usuario


# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.get("/")
def inicio():

    return {
        "mensaje": "Bienvenido a EmpleaEC"
    }


# =========================================================
# COMPROBAR CONEXIÓN
# =========================================================

@app.get("/conexion")
def comprobar_conexion():

    try:

        with engine.connect():

            return {
                "estado": "OK",
                "mensaje": "EmpleaEC está conectado a PostgreSQL"
            }

    except Exception as error:

        return {
            "estado": "ERROR",
            "mensaje": str(error)
        }


# =========================================================
# REGISTRO
# =========================================================

@app.post("/registro")
def registrar_usuario(
    usuario: schemas.UsuarioRegistro,
    db: Session = Depends(obtener_db)
):

    # Comprobar si el correo ya existe

    usuario_existente = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.email == usuario.email
        )
        .first()
    )

    if usuario_existente:

        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado"
        )

    # Comprobar tipo de usuario

    if usuario.tipo_usuario not in [
        "candidato",
        "empresa"
    ]:

        raise HTTPException(
            status_code=400,
            detail="El tipo de usuario debe ser candidato o empresa"
        )

    # Crear hash de contraseña

    password_hash = crear_hash_password(
        usuario.password
    )

    # Crear usuario

    nuevo_usuario = models.Usuario(

        nombre=usuario.nombre,

        email=usuario.email,

        password=password_hash,

        tipo_usuario=usuario.tipo_usuario

    )

    # Guardar

    db.add(nuevo_usuario)

    db.commit()

    db.refresh(nuevo_usuario)

    return {

        "mensaje": "Usuario registrado correctamente",

        "usuario": {

            "id": nuevo_usuario.id,

            "nombre": nuevo_usuario.nombre,

            "email": nuevo_usuario.email,

            "tipo_usuario": nuevo_usuario.tipo_usuario

        }

    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def iniciar_sesion(

    usuario: schemas.UsuarioLogin,

    db: Session = Depends(obtener_db)

):

    # Buscar usuario

    usuario_encontrado = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.email == usuario.email
        )
        .first()
    )

    if not usuario_encontrado:

        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    # Verificar contraseña

    contraseña_correcta = verificar_password(

        usuario.password,

        usuario_encontrado.password

    )

    if not contraseña_correcta:

        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    # Crear JWT

    token = crear_token_acceso({

        "sub": str(
            usuario_encontrado.id
        )

    })

    # Respuesta

    return {

        "mensaje": "Inicio de sesión correcto",

        "access_token": token,

        "token_type": "bearer",

        "usuario": {

            "id": usuario_encontrado.id,

            "nombre": usuario_encontrado.nombre,

            "email": usuario_encontrado.email,

            "tipo_usuario": usuario_encontrado.tipo_usuario

        }

    }


# =========================================================
# PERFIL GENERAL DEL USUARIO
# =========================================================

@app.get("/perfil")
def obtener_perfil(

    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    )

):

    return {

        "id": usuario_actual.id,

        "nombre": usuario_actual.nombre,

        "email": usuario_actual.email,

        "tipo_usuario": usuario_actual.tipo_usuario

    }


# =========================================================
# CANDIDATOS
# =========================================================


# =========================================================
# CREAR PERFIL DE CANDIDATO
# =========================================================

@app.post(
    "/candidatos/perfil",
    response_model=schemas.CandidatoRespuesta
)
def crear_perfil_candidato(

    datos: schemas.CandidatoCrear,

    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        obtener_db
    )

):

    # Comprobar que sea candidato

    if usuario_actual.tipo_usuario != "candidato":

        raise HTTPException(
            status_code=403,
            detail="Solo los candidatos pueden crear un perfil de candidato"
        )

    # Comprobar si ya tiene perfil

    perfil_existente = (
        db.query(models.Candidato)
        .filter(
            models.Candidato.usuario_id
            == usuario_actual.id
        )
        .first()
    )

    if perfil_existente:

        raise HTTPException(
            status_code=400,
            detail="Ya tienes un perfil de candidato"
        )

    # Crear perfil

    nuevo_perfil = models.Candidato(

        usuario_id=usuario_actual.id,

        telefono=datos.telefono,

        ciudad=datos.ciudad,

        provincia=datos.provincia,

        profesion=datos.profesion,

        descripcion=datos.descripcion,

        cv_url=datos.cv_url

    )

    # Guardar

    db.add(nuevo_perfil)

    db.commit()

    db.refresh(nuevo_perfil)

    return nuevo_perfil


# =========================================================
# OBTENER MI PERFIL DE CANDIDATO
# =========================================================

@app.get(
    "/candidatos/perfil",
    response_model=schemas.CandidatoRespuesta
)
def obtener_perfil_candidato(

    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        obtener_db
    )

):

    # Comprobar que sea candidato

    if usuario_actual.tipo_usuario != "candidato":

        raise HTTPException(
            status_code=403,
            detail="Solo los candidatos pueden acceder a este perfil"
        )

    # Buscar perfil

    perfil = (
        db.query(models.Candidato)
        .filter(
            models.Candidato.usuario_id
            == usuario_actual.id
        )
        .first()
    )

    if perfil is None:

        raise HTTPException(
            status_code=404,
            detail="Todavía no tienes un perfil de candidato"
        )

    return perfil


# =========================================================
# EDITAR MI PERFIL DE CANDIDATO
# =========================================================

@app.put(
    "/candidatos/perfil",
    response_model=schemas.CandidatoRespuesta
)
def editar_perfil_candidato(

    datos: schemas.CandidatoPerfil,

    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        obtener_db
    )

):

    # Comprobar que sea candidato

    if usuario_actual.tipo_usuario != "candidato":

        raise HTTPException(
            status_code=403,
            detail="Solo los candidatos pueden editar este perfil"
        )

    # Buscar perfil

    perfil = (
        db.query(models.Candidato)
        .filter(
            models.Candidato.usuario_id
            == usuario_actual.id
        )
        .first()
    )

    if perfil is None:

        raise HTTPException(
            status_code=404,
            detail="Primero debes crear tu perfil de candidato"
        )

    # Actualizar datos

    perfil.telefono = datos.telefono

    perfil.ciudad = datos.ciudad

    perfil.provincia = datos.provincia

    perfil.profesion = datos.profesion

    perfil.descripcion = datos.descripcion

    perfil.cv_url = datos.cv_url

    # Guardar cambios

    db.commit()

    db.refresh(perfil)

    return perfil

# =========================================================
# SUBIR CV
# =========================================================

@app.post("/candidatos/cv")
async def subir_cv(

    archivo: UploadFile = File(...),

    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        obtener_db
    )

):

    # -----------------------------------------------------
    # COMPROBAR QUE SEA CANDIDATO
    # -----------------------------------------------------

    if usuario_actual.tipo_usuario != "candidato":

        raise HTTPException(
            status_code=403,
            detail="Solo los candidatos pueden subir un CV"
        )

    # -----------------------------------------------------
    # COMPROBAR QUE EL ARCHIVO SEA PDF
    # -----------------------------------------------------

    if archivo.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="El CV debe estar en formato PDF"
        )

    # -----------------------------------------------------
    # BUSCAR PERFIL DEL CANDIDATO
    # -----------------------------------------------------

    candidato = (
        db.query(models.Candidato)
        .filter(
            models.Candidato.usuario_id
            == usuario_actual.id
        )
        .first()
    )

    if candidato is None:

        raise HTTPException(
            status_code=404,
            detail="Primero debes crear tu perfil de candidato"
        )

    # -----------------------------------------------------
    # CREAR NOMBRE ÚNICO
    # -----------------------------------------------------

    nombre_archivo = (
        f"{usuario_actual.id}_"
        f"{uuid.uuid4().hex}.pdf"
    )

    ruta_archivo = os.path.join(
        CARPETA_CV,
        nombre_archivo
    )

    # -----------------------------------------------------
    # GUARDAR ARCHIVO
    # -----------------------------------------------------

    contenido = await archivo.read()

    with open(
        ruta_archivo,
        "wb"
    ) as archivo_guardado:

        archivo_guardado.write(contenido)

    # -----------------------------------------------------
    # GUARDAR RUTA EN POSTGRESQL
    # -----------------------------------------------------

    candidato.cv_url = ruta_archivo

    db.commit()

    db.refresh(candidato)

    # -----------------------------------------------------
    # RESPUESTA
    # -----------------------------------------------------

    return {

        "mensaje": "CV subido correctamente",

        "archivo": nombre_archivo,

        "ruta": ruta_archivo

    }

# =========================================================
# VISUALIZAR / DESCARGAR MI CV
# =========================================================

@app.get("/candidatos/cv")
def obtener_cv(
    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    ),
    db: Session = Depends(
        obtener_db
    )
):

    # -----------------------------------------------------
    # COMPROBAR QUE SEA CANDIDATO
    # -----------------------------------------------------

    if usuario_actual.tipo_usuario != "candidato":

        raise HTTPException(
            status_code=403,
            detail="Solo los candidatos pueden acceder a su CV"
        )

    # -----------------------------------------------------
    # BUSCAR PERFIL
    # -----------------------------------------------------

    candidato = (
        db.query(models.Candidato)
        .filter(
            models.Candidato.usuario_id
            == usuario_actual.id
        )
        .first()
    )

    if candidato is None:

        raise HTTPException(
            status_code=404,
            detail="Perfil de candidato no encontrado"
        )

    # -----------------------------------------------------
    # COMPROBAR QUE TENGA CV
    # -----------------------------------------------------

    if not candidato.cv_url:

        raise HTTPException(
            status_code=404,
            detail="Todavía no has subido un CV"
        )

    # -----------------------------------------------------
    # COMPROBAR QUE EL ARCHIVO EXISTA
    # -----------------------------------------------------

    if not os.path.exists(candidato.cv_url):

        raise HTTPException(
            status_code=404,
            detail="El archivo CV no existe en el servidor"
        )

    # -----------------------------------------------------
    # DEVOLVER PDF
    # -----------------------------------------------------

    return FileResponse(
        path=candidato.cv_url,
        media_type="application/pdf",
        filename=os.path.basename(candidato.cv_url)
    )
# =========================================================
# OFERTAS DE EMPLEO
# =========================================================

@app.get("/ofertas")
def listar_ofertas(
    db: Session = Depends(obtener_db)
):

    ofertas = (
        db.query(models.OfertaEmpleo)
        .filter(
            models.OfertaEmpleo.estado == "activa"
        )
        .order_by(
            models.OfertaEmpleo.fecha_publicacion.desc()
        )
        .all()
    )

    resultado = []

    for oferta in ofertas:

        resultado.append({
            "id": oferta.id,
            "empresa_id": oferta.empresa_id,
            "titulo": oferta.titulo,
            "descripcion": oferta.descripcion,
            "requisitos": oferta.requisitos,
            "ubicacion": oferta.ubicacion,
            "tipo_empleo": oferta.tipo_empleo,
            "salario_minimo": oferta.salario_minimo,
            "salario_maximo": oferta.salario_maximo,
            "estado": oferta.estado,
            "fecha_publicacion": oferta.fecha_publicacion
        })

    return resultado

# =========================================================
# EMPRESAS
# =========================================================


# ---------------------------------------------------------
# CREAR PERFIL DE EMPRESA
# ---------------------------------------------------------

@app.post(
    "/empresas/perfil",
    response_model=schemas.EmpresaRespuesta
)
def crear_perfil_empresa(

    datos: schemas.EmpresaCrear,

    usuario_actual: models.Usuario = Depends(
        obtener_usuario_actual
    ),

    db: Session = Depends(
        obtener_db
    )

):

    # Comprobar que sea empresa

    if usuario_actual.tipo_usuario != "empresa":

        raise HTTPException(
            status_code=403,
            detail="Solo las empresas pueden crear un perfil empresarial"
        )

    # Comprobar si ya existe

    perfil_existente = (
        db.query(models.Empresa)
        .filter(
            models.Empresa.usuario_id == usuario_actual.id
        )
        .first()
    )

    if perfil_existente:

        raise HTTPException(
            status_code=400,
            detail="Ya tienes un perfil empresarial"
        )

    # Crear perfil

    nueva_empresa = models.Empresa(

        usuario_id=usuario_actual.id,

        nombre_empresa=datos.nombre_empresa,

        descripcion=datos.descripcion,

        telefono=datos.telefono,

        ciudad=datos.ciudad,

        provincia=datos.provincia,

        direccion=datos.direccion,

        sitio_web=datos.sitio_web

    )

    db.add(nueva_empresa)

    db.commit()

    db.refresh(nueva_empresa)

    return nueva_empresa
