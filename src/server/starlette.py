from starlette.requests import Request
from starlette.routing import Route
from starlette.responses import Response, JSONResponse
from ariadne.asgi import GraphQL

from src.quote.quote import Service as QuoteService
from src.heartbeat.heartbeat import Service as HeartbeatService
from src.server.graphql.schema import get_schema


class Handlers:
    def __init__(self, quotes: QuoteService, heartbeat: HeartbeatService):
        self.quotes = quotes
        self.heartbeat = heartbeat
        self.graphql_app = GraphQL(get_schema(), context_value=self.__get_context_value)

        self.routes = []
        self.routes.append(Route("/", self.get_quote_handler, methods=["GET"]))
        self.routes.append(Route("/heartbeat", self.heartbeat_handler, methods=["GET"]))
        self.routes.append(Route("/same", self.get_same_quote_handler, methods=["GET"]))
        self.routes.append(Route("/like", self.like_quote_handler, methods=["PATCH"]))
        self.routes.append(Route("/graphql", self.graphql, methods=["GET", "POST"]))

    async def get_quote_handler(self, request: Request):
        user_id = request.query_params["user_id"]
        return JSONResponse(self.quotes.get_quote(user_id).model_dump())

    async def heartbeat_handler(self, request: Request):
        self.heartbeat.ping_database()
        return Response()

    async def get_same_quote_handler(self, request: Request):
        user_id = request.query_params["user_id"]
        quote_id = request.query_params["quote_id"]
        return JSONResponse(self.quotes.get_same_quote(user_id, quote_id).model_dump())

    async def like_quote_handler(self, request: Request):
        user_id = request.query_params["user_id"]
        quote_id = request.query_params["quote_id"]
        self.quotes.like_quote(user_id, quote_id)
        return Response()

    async def graphql_explorer(self, request: Request):
        return await self.graphql_app.handle_request(request)

    async def graphql(self, request: Request):
        return await self.graphql_app.handle_request(request)

    def __get_context_value(self, request: Request, _data) -> dict:
        return {
            "request": request,
            "heartbeat": self.heartbeat,
            "quotes": self.quotes,
        }
