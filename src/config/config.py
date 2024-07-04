from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseSettings):
    server: str = Field(alias="SERVER", default="fastapi")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class PostgresConfig(BaseSettings):
    orm: str = Field(alias="POSTGRES_ORM", default="sqlalchemy")
    dsn: str = Field(alias="POSTGRES_DSN")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class QuotesConfig(BaseSettings):
    random_quote_chance: float = Field(alias="RANDOM_QUOTE_CHANCE", default=20.0)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
