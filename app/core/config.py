import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60
    lci_service_api_url: str

    model_config = SettingsConfigDict(env_file=".env")


if not os.path.exists(".env"):
    raise FileNotFoundError(
        "O arquivo '.env' não foi encontrado. Certifique-se de que ele existe na raiz do projeto."
    )
