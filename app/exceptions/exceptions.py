from fastapi import HTTPException, status


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Token inválido"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class LCIServiceException(HTTPException):
    def __init__(
        self,
        detail: str = "Erro no serviço LCI",
        status_code: int = status.HTTP_502_BAD_GATEWAY,
    ):
        super().__init__(status_code=status_code, detail=detail)
