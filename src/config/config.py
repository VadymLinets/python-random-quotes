from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class ServerConfig(Config):
    server: str = Field(alias="SERVER", default="fastapi")
    grpc_port: int = Field(alias="GRPC_PORT", default=1140)


class PostgresConfig(Config):
    orm: str = Field(alias="POSTGRES_ORM", default="sqlalchemy")
    dsn: str = Field(alias="POSTGRES_DSN")


class QuotesConfig(Config):
    random_quote_chance: float = Field(alias="RANDOM_QUOTE_CHANCE", default=20.0)
