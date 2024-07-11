from fastapi import APIRouter, Request
from ariadne.asgi import GraphQL
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers,
    ObjectType,
)

from src.quote.quote import Service as QuoteService
from src.heartbeat.heartbeat import Service as HeartbeatService
from src.server.graphql.resolvers import (
    heartbeat_resolver,
    get_quote_resolver,
    get_same_quote_resolver,
    like_quote_resolver,
)


def get_context_value(request: Request, _data) -> dict:
    return {
        "request": request,
        "heartbeat": request.scope["heartbeat"],
        "quotes": request.scope["quotes"],
    }


class Handlers:
    def __init__(self, quotes: QuoteService, heartbeat: HeartbeatService):
        self.quotes = quotes
        self.heartbeat = heartbeat

        query = ObjectType("QueryHandler")
        query.set_field("heartbeat", heartbeat_resolver)
        query.set_field("get_quote_handler", get_quote_resolver)
        query.set_field("get_same_quote_handler", get_same_quote_resolver)

        mutation = ObjectType("MutationHandler")
        mutation.set_field("like_quote_handler", like_quote_resolver)

        type_defs = load_schema_from_path("schema.graphql")
        schema = make_executable_schema(
            type_defs, query, mutation, snake_case_fallback_resolvers
        )
        self.graphql_app = GraphQL(schema, context_value=get_context_value)

        self.router = APIRouter()
        self.router.add_api_route("/", self.get_quote_handler, methods=["GET"])
        self.router.add_api_route("/heartbeat", self.heartbeat_handler, methods=["GET"])
        self.router.add_api_route("/same", self.get_same_quote_handler, methods=["GET"])
        self.router.add_api_route("/like", self.like_quote_handler, methods=["PATCH"])

        self.router.options("/graphql")
        self.router.add_api_route("/graphql", self.graphql_explorer, methods=["GET"])
        self.router.add_api_route("/graphql", self.graphql_query, methods=["POST"])

    async def get_quote_handler(self, user_id: str):
        return self.quotes.get_quote(user_id)

    async def heartbeat_handler(self):
        self.heartbeat.ping_database()

    async def get_same_quote_handler(self, user_id: str, quote_id: str):
        return self.quotes.get_same_quote(user_id, quote_id)

    async def like_quote_handler(self, user_id: str, quote_id: str):
        return self.quotes.like_quote(user_id, quote_id)

    async def graphql_explorer(self, request: Request):
        return await self.graphql_app.handle_request(request)

    async def graphql_query(self, request: Request):
        request.scope["heartbeat"] = self.heartbeat
        request.scope["quotes"] = self.quotes
        return await self.graphql_app.handle_request(request)
