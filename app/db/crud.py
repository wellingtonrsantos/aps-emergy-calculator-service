from sqlmodel import Session, select
from app.db.models import User
from typing import Optional
from app.core.security import (
    generate_password_hash,
)
from app.models.authentication import RegisterRequest


def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = session.exec(statement).first()
    return result


def create_user(session: Session, user_request: RegisterRequest) -> User:
    hashed_password = generate_password_hash(user_request.password)
    user = User(
        name=user_request.name,
        surname=user_request.surname,
        email=user_request.email,
        hashed_password=hashed_password,
        mobile_number=user_request.mobile_number,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
