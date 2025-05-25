from datetime import datetime, timedelta, timezone
from jose import jwt
from app.db.models import User
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.exceptions.exceptions import UnauthorizedException
from app.core.logger import logger
from app.core.config import Settings
from functools import lru_cache
from app.core.security import verify_password
from app.service.user_service import UserService


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(session: Session, email: str, password: str) -> User:
    logger.info(f"Autenticando usuário com email: {email}")
    user_service = UserService(session)
    user = user_service.get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"Usuário com email {email} não encontrado.")
        return None
    logger.info(f"Usuário autenticado com sucesso: {email}")
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    logger.info("Validando token JWT.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning(f"Token inválido: campo 'sub' ausente. [{email}]")
            raise UnauthorizedException()
        return email
    except JWTError as e:
        logger.error(f"Erro ao decodificar o token JWT: {e}")
        raise UnauthorizedException()


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
