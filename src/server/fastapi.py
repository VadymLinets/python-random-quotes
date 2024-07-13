from fastapi import APIRouter, Request
from ariadne.asgi import GraphQL

from src.quote.quote import Service as QuoteService
from src.heartbeat.heartbeat import Service as HeartbeatService
from src.server.graphql.schema import get_schema


class Handlers:
    def __init__(self, quotes: QuoteService, heartbeat: HeartbeatService):
        self.quotes = quotes
        self.heartbeat = heartbeat
        self.graphql_app = GraphQL(get_schema(), context_value=self.__get_context_value)

        self.router = APIRouter()
        self.router.add_api_route("/", self.get_quote_handler, methods=["GET"])
        self.router.add_api_route("/heartbeat", self.heartbeat_handler, methods=["GET"])
        self.router.add_api_route("/same", self.get_same_quote_handler, methods=["GET"])
        self.router.add_api_route("/like", self.like_quote_handler, methods=["PATCH"])

        self.router.options("/graphql")
        self.router.add_api_route("/graphql", self.graphql, methods=["GET", "POST"])

    async def get_quote_handler(self, user_id: str):
        return self.quotes.get_quote(user_id)

    async def heartbeat_handler(self):
        self.heartbeat.ping_database()

    async def get_same_quote_handler(self, user_id: str, quote_id: str):
        return self.quotes.get_same_quote(user_id, quote_id)

    async def like_quote_handler(self, user_id: str, quote_id: str):
        return self.quotes.like_quote(user_id, quote_id)

    async def graphql(self, request: Request):
        return await self.graphql_app.handle_request(request)

    def __get_context_value(self, request: Request, _data) -> dict:
        return {
            "request": request,
            "heartbeat": self.heartbeat,
            "quotes": self.quotes,
        }
