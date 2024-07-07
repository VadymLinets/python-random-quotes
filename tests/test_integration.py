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

postgres: PostgresContainer
db: sqlalchemy.Postgres
client: TestClient
fake = Faker()


def setup_module():
    global postgres
    global db
    global client

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

    db = sqlalchemy.Postgres(postgres_config)

    quotes_cfg = cfg.QuotesConfig()
    quotes_cfg.random_quote_chance = 0.0

    quote_api = api.Service(db)
    quotes_service = quote_srv.Service(quotes_cfg, db, quote_api)
    heartbeat_service = heartbeat.Service(db)

    app = FastAPI()
    h = fastapi_handlers.Handlers(quotes_service, heartbeat_service)
    app.include_router(h.router)

    client = TestClient(app)


def teardown_module():
    postgres.stop(delete_volume=True)


class TestIntegration:
    @pytest.fixture(scope="module")
    def quote(self) -> Quote:
        return Quote(
            quote_id=fake.uuid4(cast_to=str),
            quote=fake.sentence(nb_words=20, variable_nb_words=True),
            author=fake.name(),
            tags=[fake.color(), fake.color()],
        )

    @pytest.fixture(scope="module")
    def user_id(self) -> str:
        return fake.uuid4(cast_to=str)

    def test_get_quote(self, quote, user_id):
        db.save_quote(quote)
        response = client.get(url="/", params={"user_id": user_id})
        assert response.status_code == 200
        assert response.json() == quote.__dict__

        db_quote = db.get_quote(quote.id)
        assert quote == db_quote

    def test_like_quote(self, quote, user_id):
        response = client.patch(
            url="/like", params={"user_id": user_id, "quote_id": quote.id}
        )
        assert response.status_code == 200

        db_quote = db.get_quote(quote.id)
        assert 1 == db_quote.likes

    def test_get_same_quote(self, quote, user_id):
        same_quote = Quote(
            quote_id=fake.uuid4(cast_to=str),
            quote=fake.sentence(nb_words=20, variable_nb_words=True),
            author=quote.author,
            tags=quote.tags,
        )

        random_quote = Quote(
            quote_id=fake.uuid4(cast_to=str),
            quote=fake.sentence(nb_words=20, variable_nb_words=True),
            author=fake.name(),
            tags=[fake.color(), fake.color()],
        )

        db.save_quote(same_quote)
        db.save_quote(random_quote)

        response = client.get(
            url="/same", params={"user_id": user_id, "quote_id": quote.id}
        )
        assert response.status_code == 200
        assert response.json() == same_quote.__dict__
