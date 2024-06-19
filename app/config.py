from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    
    # Optional settings for local development
    app_port: Optional[int] = 8000
    db_port: Optional[int] = 3306
    mariadb_root_password: Optional[str]
    mariadb_user: Optional[str]
    mariadb_password: Optional[str]
    mariadb_database: Optional[str]

    class Config:
        env_file = ".env"

settings = Settings()