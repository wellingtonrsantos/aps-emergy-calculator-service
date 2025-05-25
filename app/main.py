from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.exception_handler import (
    custom_http_exception_handler,
    validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarlletteHTTPException
from app.routes import calculate, authetication, lci
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# Configuração do esquema OAuth2 para o Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

app = FastAPI(title="Calculadora de Emergia API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StarlletteHTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(
    authetication.router, prefix="/api/auth", tags=["Cadastro e Autenticação"]
)
app.include_router(lci.router, prefix="/api/lci", tags=["Dados LCI"])
app.include_router(calculate.router, prefix="/api/calculate", tags=["Cálculo"])


# Configuração do esquema de segurança no Swagger para realizar a autenticação
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API para Calculadora de Emergia",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
