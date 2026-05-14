"""
Config Settings
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings"""

    CLOUD_STORAGE_DEPOSITO_EDICTOS: str = ""
    CLOUD_STORAGE_DEPOSITO_GLOSAS: str = ""
    CLOUD_STORAGE_DEPOSITO_LISTAS_DE_ACUERDOS: str = ""
    CLOUD_STORAGE_DEPOSITO_OFICIOS: str = ""
    CLOUD_STORAGE_DEPOSITO_SENTENCIAS: str = ""
    CLOUD_STORAGE_DEPOSITO_VSP_DIGITALIZACIONES: str = ""
    DB_USER: str = "username"
    DB_PASS: str = "password"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "database"
    SALT: str = "some_random_salt"
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    class Config:
        """Config"""

        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get settings"""
    return Settings()
