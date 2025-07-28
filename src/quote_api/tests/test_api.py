import pytest
import responses
import sys

import src.quote_api.api as quote_api_srv
import src.config.config as cfg
import src.database.sqlalchemy as sqlalchemy

sys.path.append("../../../src")


@pytest.fixture
def quote():
    return quote_api_srv.Quote(
        id="956",
        quote="Time Stays Long Enough For Anyone Who Will Use It.",
        author="Leonardo Da Vinci",
    )


@responses.activate
def test_get_random_quote_success(mocker, quote):
    db = sqlalchemy.Postgres(cfg.PostgresConfig(POSTGRES_DSN="sqlite:///:memory:"))
    mocker.patch.object(db, "save_quote", return_value=None)

    responses.patch(quote_api_srv.random_quote_url)
    responses._add_from_file(file_path="src/quote_api/tests/testdata/responses.yaml")
    responses.get(quote_api_srv.random_quote_url)

    srv = quote_api_srv.Service(db)
    assert quote.__dict__ == srv.get_random_quote().__dict__
