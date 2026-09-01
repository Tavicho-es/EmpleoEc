import bcrypt


def crear_hash_password(password: str):
    password_bytes = password.encode("utf-8")
    
    return bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    ).decode("utf-8")


def verificar_password(password: str, password_hash: str):
    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        hash_bytes
    )

from datetime import datetime, timedelta
from jose import JWTError, jwt


# Clave secreta para firmar los tokens (cámbiala por algo único y largo)
SECRET_KEY = "cambia-esta-clave-por-una-cadena-larga-y-aleatoria"
ALGORITHM = "HS256"
EXPIRACION_MINUTOS = 60 * 24  # El token dura 1 día


def crear_token_acceso(datos: dict):
    datos_copia = datos.copy()

    expiracion = datetime.utcnow() + timedelta(minutes=EXPIRACION_MINUTOS)
    datos_copia.update({"exp": expiracion})

    return jwt.encode(datos_copia, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError:
        return None