import pytest
import sys
from faker import Faker

sys.path.append("../../../src")

import src.quote.quote as quote_srv
import src.quote_api.api as quote_api_srv
import src.config.config as cfg
import src.database.sqlalchemy as sqlalchemy
from src.quote.models import Quote, View

fake = Faker()


@pytest.fixture
def quote():
    return Quote(
        id=fake.uuid4(cast_to=str),
        quote=fake.sentence(nb_words=20, variable_nb_words=True),
        author=fake.name(),
        tags=fake.get_words_list(),
        likes=0,
    )


@pytest.fixture
def view():
    return View(
        quote_id=fake.uuid4(cast_to=str), user_id=fake.uuid4(cast_to=str), liked=False
    )


@pytest.fixture
def user_id() -> str:
    return fake.uuid4(cast_to=str)


def test_get_quote_success(mocker, quote, user_id):
    db = sqlalchemy.Postgres(cfg.PostgresConfig())
    mocker.patch.object(db, "get_quotes", return_value=[quote])
    mocker.patch.object(db, "mark_as_viewed", return_value=None)

    quote_cfg = cfg.QuotesConfig()
    quote_cfg.random_quote_chance = 0.0
    srv = quote_srv.Service(quote_cfg, db, None)
    assert quote == srv.get_quote(user_id)


def test_get_quote_success_random(mocker, quote, user_id):
    db = sqlalchemy.Postgres(cfg.PostgresConfig())
    mocker.patch.object(db, "get_quotes", return_value=[])
    mocker.patch.object(db, "mark_as_viewed", return_value=None)

    api = quote_api_srv.Service(db)
    mocker.patch.object(api, "get_random_quote", return_value=quote)

    quote_cfg = cfg.QuotesConfig()
    quote_cfg.random_quote_chance = 100.0
    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote == srv.get_quote(user_id)


def test_like_quote_success(mocker, view):
    db = sqlalchemy.Postgres(cfg.PostgresConfig())
    mocker.patch.object(db, "get_view", return_value=view)
    mocker.patch.object(db, "like_quote", return_value=None)
    mocker.patch.object(db, "mark_as_liked", return_value=None)

    srv = quote_srv.Service(None, db, None)
    assert srv.like_quote(quote_id=view.quote_id, user_id=view.user_id) is None


def test_like_quote_already_liked(mocker, view):
    view.liked = True

    db = sqlalchemy.Postgres(cfg.PostgresConfig())
    mocker.patch.object(db, "get_view", return_value=view)

    srv = quote_srv.Service(None, db, None)
    assert srv.like_quote(quote_id=view.quote_id, user_id=view.user_id) is None


def test_get_same_quote_success(mocker, quote, user_id):
    db = sqlalchemy.Postgres(cfg.PostgresConfig())
    mocker.patch.object(db, "get_quote", return_value=quote)
    mocker.patch.object(db, "get_same_quote", return_value=quote)
    mocker.patch.object(db, "mark_as_viewed", return_value=None)

    srv = quote_srv.Service(None, db, None)
    assert quote == srv.get_same_quote(user_id=user_id, quote_id=quote.id)


def test_get_same_quote_random(mocker, quote, user_id):
    db = sqlalchemy.Postgres(cfg.PostgresConfig())
    mocker.patch.object(db, "get_quote", return_value=quote)
    mocker.patch.object(db, "get_same_quote", return_value=None)
    mocker.patch.object(db, "mark_as_viewed", return_value=None)

    api = quote_api_srv.Service(db)
    mocker.patch.object(api, "get_random_quote", return_value=quote)

    srv = quote_srv.Service(None, db, api)
    assert quote == srv.get_same_quote(user_id=user_id, quote_id=quote.id)
