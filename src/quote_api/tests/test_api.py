import pytest
import responses

import sys

sys.path.append("../../../src")

import src.quote_api.api as quote_api_srv
import src.config.config as cfg
import src.database.sqlalchemy as sqlalchemy


@pytest.fixture
def quote():
    return quote_api_srv.Quote(
        id="r3wAKE9N-Nei",
        quote="Imagination will often carry us to worlds that never were. But without it we go nowhere.",
        author="Carl Sagan",
        tags=["Famous Quotes"],
        likes=0,
    )


@responses.activate
def test_get_random_quote_success(mocker, quote):
    db = sqlalchemy.Postgres(cfg.PostgresConfig())
    mocker.patch.object(db, "save_quote", return_value=None)

    responses.patch(quote_api_srv.random_quote_url)
    responses._add_from_file(file_path="src/quote_api/tests/testdata/responses.yaml")
    responses.get(quote_api_srv.random_quote_url)

    srv = quote_api_srv.Service(db)
    assert quote.__dict__ == srv.get_random_quote().__dict__
