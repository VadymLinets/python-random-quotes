import requests
# from responses import _recorder

from src.quote.interfaces import APIInterface
from src.quote_api.interfaces import DBInterface, Quote

random_quote_url = "https://dummyjson.com/quotes/random"


class Service(APIInterface):
    def __init__(self, db: DBInterface):
        self.db = db

    # @_recorder.record(file_path="src/quote_api/tests/testdata/responses.yaml")
    def get_random_quote(self) -> Quote:
        resp = requests.get(random_quote_url)
        random_quote = resp.json()
        quote = Quote(
            id=str(random_quote["id"]),
            quote=random_quote["quote"],
            author=random_quote["author"],
            # tags=random_quote["tags"],
        )
        self.db.save_quote(quote)
        return quote
