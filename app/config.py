from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    app_port: int
    db_port: int
    mariadb_root_password: str
    mariadb_user: str
    mariadb_password: str
    mariadb_database: str
    openai_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()
