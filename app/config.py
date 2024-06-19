from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Required settings
    database_url: str
    openai_api_key: str

    # Optional settings for local development or other purposes
    app_port: Optional[int] = 8000
    db_port: Optional[int] = 3306
    mariadb_root_password: Optional[str] = None
    mariadb_user: Optional[str] = "default_user"
    mariadb_password: Optional[str] = "default_password"
    mariadb_database: Optional[str] = "default_database"

    class Config:
        env_file = ".env"


settings = Settings()
