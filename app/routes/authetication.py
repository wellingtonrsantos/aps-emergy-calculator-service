from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.core.auth import create_access_token, authenticate_user, decode_access_token
from app.core.logger import logger
from app.models.authentication import LoginRequest, RegisterRequest, UserResponse
from app.exceptions.exceptions import UnauthorizedException
from app.service.user_service import UserService

router = APIRouter()
security = HTTPBearer()


@router.post("/register")
async def register_user(
    register_request: RegisterRequest, session: Session = Depends(get_session)
) -> dict:
    user_service = UserService(session)
    user = user_service.create_user(register_request)
    return {"message": "Usuário registrado com sucesso", "user_id": user.id}


@router.post("/login")
async def login(
    login_request: LoginRequest,
    session: Session = Depends(get_session),
) -> dict:
    user = authenticate_user(session, login_request.email, login_request.password)
    if not user:
        raise UnauthorizedException(detail="Credenciais inválidas")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(security), session: Session = Depends(get_session)
) -> UserResponse:
    try:
        email = decode_access_token(token.credentials)
        if not email:
            raise UnauthorizedException(detail="Could not validate credentials")

        user_service = UserService(session)
        user = user_service.get_user_by_email(email)

        if not user:
            raise UnauthorizedException(detail="User not found")

        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            surname=user.surname,
            mobile_number=user.mobile_number,
        )
    except Exception:
        logger.error(f"Erro ao buscar informações do usuario[{email}]: ", exc_info=True)
        raise UnauthorizedException(detail="Could not validate credentials")
