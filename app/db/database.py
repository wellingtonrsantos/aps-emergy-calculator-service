from sqlmodel import SQLModel, create_engine, Session
from app.core.logger import logger
from app.core.config import Settings
from functools import lru_cache


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized successfully.")


def get_session():
    with Session(engine) as session:
        yield session
