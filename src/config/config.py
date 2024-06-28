from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class PostgresConfig(BaseSettings):
    dsn: str = Field(alias="POSTGRES_DSN")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


class QuotesConfig(BaseSettings):
    random_quote_chance: float = Field(20.0, alias="RANDOM_QUOTE_CHANCE")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
