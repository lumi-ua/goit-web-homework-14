from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_db: str 
    postgres_user: str 
    postgres_password: str 
    postgres_port: int 
    sqlalchemy_database_url: str = 'postgresql+psycopg2://user:password@localhost:5432/postgres'
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    mail_username: str = 'example@meta.ua'
    mail_password: str = 'password'
    mail_from: str = 'example@meta.ua'
    mail_port: int = 465
    mail_server: str = 'smtp.meta.ua'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str 
    cloudinary_api_key: str 
    cloudinary_api_secret: str 

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",case_sensitive=False)


settings = Settings()
