import pytest
import os
import subprocess

from faker import Faker
from fastapi import FastAPI
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

import src.config.config as cfg
import src.database.sqlalchemy as sqlalchemy
import src.heartbeat.heartbeat as heartbeat
import src.quote_api.api as api
import src.quote.quote as quote_srv
import src.server.fastapi as fastapi_handlers
from src.quote.models import Quote


class TestIntegration:
    fake = Faker()

    @pytest.fixture
    def quote(self) -> Quote:
        return Quote(
            id=self.fake.uuid4(cast_to=str),
            quote=self.fake.sentence(nb_words=20, variable_nb_words=True),
            author=self.fake.name(),
            tags=[self.fake.color(), self.fake.color()],
        )

    @pytest.fixture
    def user_id(self) -> str:
        return self.fake.uuid4(cast_to=str)

    @pytest.fixture(autouse=True)
    def run_essentials(
        self, quote
    ) -> (sqlalchemy.Postgres, TestClient, PostgresContainer):
        postgres = PostgresContainer(
            image="docker.io/postgres:16-alpine",
            username="postgres",
            password="postgres",
            dbname="test_quotes",
        )
        postgres.start()

        os.environ["POSTGRES_DSN"] = postgres.get_connection_url()
        subprocess.run(["alembic", "upgrade", "head"])

        postgres_config = cfg.PostgresConfig()
        postgres_config.dsn = postgres.get_connection_url()

        self.db = sqlalchemy.Postgres(postgres_config)
        self.db.save_quote(quote)

        quotes_cfg = cfg.QuotesConfig()
        quotes_cfg.random_quote_chance = 0.0

        quote_api = api.Service(self.db)
        quotes_service = quote_srv.Service(quotes_cfg, self.db, quote_api)
        heartbeat_service = heartbeat.Service(self.db)

        app = FastAPI()
        h = fastapi_handlers.Handlers(quotes_service, heartbeat_service)
        app.include_router(h.router)

        self.client = TestClient(app)

        yield

        postgres.stop(delete_volume=True)

    def test_get_quote(self, quote, user_id):
        response = self.client.get(url="/", params={"user_id": user_id})
        assert response.status_code == 200
        assert response.json() == quote.__dict__

        db_quote = self.db.get_quote(quote.id)
        assert quote == db_quote

    def test_like_quote(self, quote, user_id):
        self.db.mark_as_viewed(quote_id=quote.id, user_id=user_id)
        response = self.client.patch(
            url="/like", params={"user_id": user_id, "quote_id": quote.id}
        )
        assert response.status_code == 200

        db_quote = self.db.get_quote(quote.id)
        assert 1 == db_quote.likes

    def test_get_same_quote(self, quote, user_id):
        self.db.mark_as_viewed(quote_id=quote.id, user_id=user_id)
        same_quote = Quote(
            id=self.fake.uuid4(cast_to=str),
            quote=self.fake.sentence(nb_words=20, variable_nb_words=True),
            author=quote.author,
            tags=quote.tags,
            likes=0,
        )

        random_quote = Quote(
            id=self.fake.uuid4(cast_to=str),
            quote=self.fake.sentence(nb_words=20, variable_nb_words=True),
            author=self.fake.name(),
            tags=[self.fake.color(), self.fake.color()],
            likes=0,
        )

        self.db.save_quote(same_quote)
        self.db.save_quote(random_quote)

        response = self.client.get(
            url="/same", params={"user_id": user_id, "quote_id": quote.id}
        )
        assert response.status_code == 200
        assert response.json() == same_quote.__dict__
