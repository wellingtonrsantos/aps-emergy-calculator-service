from app.db.models import User
from app.db.crud import get_user_by_email, create_user
from app.models.authentication import RegisterRequest
from sqlmodel import Session
from app.exceptions.exceptions import BadRequestException


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str) -> User | None:
        return get_user_by_email(self.session, email)

    def create_user(self, register_request: RegisterRequest) -> User:
        existing_user = self.get_user_by_email(register_request.email)
        if existing_user:
            raise BadRequestException("Email já está em uso")

        return create_user(self.session, register_request)
