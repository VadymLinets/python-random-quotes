from fastapi import APIRouter
from src.quote.quote import Service as quote_srv
from src.heartbeat.heartbeat import Service as heartbeat_srv


class Handlers:
    def __init__(self, quotes: quote_srv, heartbeat: heartbeat_srv):
        self.quotes = quotes
        self.heartbeat = heartbeat

        self.router = APIRouter()
        self.router.add_api_route("/", self.get_quote_handler, methods=["GET"])
        self.router.add_api_route("/heartbeat", self.heartbeat_handler, methods=["GET"])
        self.router.add_api_route("/same", self.get_same_quote_handler, methods=["GET"])
        self.router.add_api_route("/like", self.like_quote_handler, methods=["PATCH"])

    async def get_quote_handler(self, user_id: str):
        return self.quotes.get_quote(user_id)

    async def heartbeat_handler(self):
        self.heartbeat.ping_database()

    async def get_same_quote_handler(self, user_id: str, quote_id: str):
        return self.quotes.get_same_quote(user_id, quote_id)

    async def like_quote_handler(self, user_id: str, quote_id: str):
        return self.quotes.like_quote(user_id, quote_id)
