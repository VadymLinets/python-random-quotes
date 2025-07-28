import pytest
import sys
from faker import Faker

import src.quote.quote as quote_srv
import src.quote_api.api as quote_api_srv
import src.config.config as cfg
import src.database.sqlalchemy as sqlalchemy
from src.quote.models import Quote, View

sys.path.append("../../../src")
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
    quote_cfg, db, api = get_services()
    quote_cfg.random_quote_chance = 0.0
    mocker.patch.object(db, "get_quotes", return_value=[quote])
    mocker.patch.object(db, "mark_as_viewed", return_value=None)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote == srv.get_quote(user_id)


def test_get_quote_success_random(mocker, quote, user_id):
    quote_cfg, db, api = get_services()
    quote_cfg.random_quote_chance = 100.0
    mocker.patch.object(db, "get_quotes", return_value=[])
    mocker.patch.object(db, "mark_as_viewed", return_value=None)
    mocker.patch.object(api, "get_random_quote", return_value=quote)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote == srv.get_quote(user_id)


def test_like_quote_success(mocker, view):
    quote_cfg, db, api = get_services()
    mocker.patch.object(db, "get_view", return_value=view)
    mocker.patch.object(db, "like_quote", return_value=None)
    mocker.patch.object(db, "mark_as_liked", return_value=None)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert srv.like_quote(quote_id=view.quote_id, user_id=view.user_id) is None


def test_like_quote_already_liked(mocker, view):
    quote_cfg, db, api = get_services()
    view.liked = True
    mocker.patch.object(db, "get_view", return_value=view)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert srv.like_quote(quote_id=view.quote_id, user_id=view.user_id) is None


def test_like_quote_no_view(mocker, view):
    quote_cfg, db, api = get_services()
    mocker.patch.object(db, "get_view", return_value=None)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert srv.like_quote(quote_id=view.quote_id, user_id=view.user_id) is None


def test_get_same_quote_success(mocker, quote, user_id):
    quote_cfg, db, api = get_services()
    mocker.patch.object(db, "get_quote", return_value=quote)
    mocker.patch.object(db, "get_same_quote", return_value=quote)
    mocker.patch.object(db, "mark_as_viewed", return_value=None)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote == srv.get_same_quote(user_id=user_id, quote_id=quote.id)


def test_get_same_quote_random(mocker, quote, user_id):
    quote_cfg, db, api = get_services()
    mocker.patch.object(db, "get_quote", return_value=quote)
    mocker.patch.object(db, "get_same_quote", return_value=None)
    mocker.patch.object(db, "mark_as_viewed", return_value=None)
    mocker.patch.object(api, "get_random_quote", return_value=quote)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote == srv.get_same_quote(user_id=user_id, quote_id=quote.id)


def test_choose_quote_success():
    quote_1 = Quote(
        id=fake.uuid4(cast_to=str),
        quote=fake.sentence(nb_words=20, variable_nb_words=True),
        author=fake.name(),
        tags=fake.get_words_list(),
        likes=10,
    )

    quote_2 = Quote(
        id=fake.uuid4(cast_to=str),
        quote=fake.sentence(nb_words=20, variable_nb_words=True),
        author=fake.name(),
        tags=fake.get_words_list(),
        likes=90,
    )

    quote_cfg, db, api = get_services()
    quote_cfg.random_quote_chance = 0.0
    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote_1 == srv.choose_quote([quote_1, quote_2], 10.0)
    assert quote_2 == srv.choose_quote([quote_1, quote_2], 11.0)


def test_choose_quote_zero_likes():
    quote_1 = Quote(
        id=fake.uuid4(cast_to=str),
        quote=fake.sentence(nb_words=20, variable_nb_words=True),
        author=fake.name(),
        tags=fake.get_words_list(),
    )

    quote_2 = Quote(
        id=fake.uuid4(cast_to=str),
        quote=fake.sentence(nb_words=20, variable_nb_words=True),
        author=fake.name(),
        tags=fake.get_words_list(),
    )

    quote_cfg, db, api = get_services()
    quote_cfg.random_quote_chance = 0.0
    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote_1 == srv.choose_quote(quotes=[quote_1, quote_2])
    assert quote_2 == srv.choose_quote([quote_1, quote_2], 51.0)


def test_choose_quote_random(mocker, quote):
    quote_1 = Quote(
        id=fake.uuid4(cast_to=str),
        quote=fake.sentence(nb_words=20, variable_nb_words=True),
        author=fake.name(),
        tags=fake.get_words_list(),
        likes=1,
    )

    quote_2 = Quote(
        id=fake.uuid4(cast_to=str),
        quote=fake.sentence(nb_words=20, variable_nb_words=True),
        author=fake.name(),
        tags=fake.get_words_list(),
        likes=1,
    )

    quote_cfg, db, api = get_services()
    quote_cfg.random_quote_chance = 1.0
    mocker.patch.object(api, "get_random_quote", return_value=quote)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote == srv.choose_quote([quote_1, quote_2], 99.0)
    assert quote_2 == srv.choose_quote([quote_1, quote_2], 98.0)
    assert quote_1 == srv.choose_quote([quote_1, quote_2], 21.0)

    quote_cfg.random_quote_chance = 98.0
    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote == srv.choose_quote([quote_1, quote_2], 60.0)
    assert quote_2 == srv.choose_quote([quote_1, quote_2], 1.9)
    assert quote_1 == srv.choose_quote([quote_1, quote_2], 0.0)


def test_choose_quote_empty_list(mocker, quote):
    quote_cfg, db, api = get_services()
    quote_cfg.random_quote_chance = 80.0
    mocker.patch.object(api, "get_random_quote", return_value=quote)

    srv = quote_srv.Service(quote_cfg, db, api)
    assert quote == srv.choose_quote([], 19.0)
    assert quote == srv.choose_quote(quotes=[])


def get_services() -> (cfg.QuotesConfig, sqlalchemy.Postgres, quote_api_srv.Service):
    quote_cfg = cfg.QuotesConfig()
    db = sqlalchemy.Postgres(cfg.PostgresConfig(dsn="sqlite:///:memory:"))
    api = quote_api_srv.Service(db)
    return quote_cfg, db, api
