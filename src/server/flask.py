from ariadne.explorer import ExplorerGraphiQL
from flask import Blueprint, request, jsonify
from ariadne import (
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers,
    ObjectType,
    graphql_sync,
)

from src.quote.quote import Service as QuoteService
from src.heartbeat.heartbeat import Service as HeartbeatService
from src.server.graphql.resolvers import (
    heartbeat_resolver,
    get_quote_resolver,
    get_same_quote_resolver,
    like_quote_resolver,
)


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
        self.schema = make_executable_schema(
            type_defs, query, mutation, snake_case_fallback_resolvers
        )
        self.explorer_html = ExplorerGraphiQL().html(None)

        self.router = Blueprint("quotes", __name__)
        self.router.add_url_rule("/", view_func=self.get_quote_handler, methods=["GET"])
        self.router.add_url_rule(
            "/heartbeat", view_func=self.heartbeat_handler, methods=["GET"]
        )
        self.router.add_url_rule(
            "/same", view_func=self.get_same_quote_handler, methods=["GET"]
        )
        self.router.add_url_rule(
            "/like", view_func=self.like_quote_handler, methods=["PATCH"]
        )

        self.router.add_url_rule(
            "/graphql", view_func=self.graphql_explorer, methods=["GET"]
        )
        self.router.add_url_rule(
            "/graphql", view_func=self.graphql_query, methods=["POST"]
        )

    async def get_quote_handler(self):
        return self.quotes.get_quote(request.args.get("user_id")).__dict__

    async def heartbeat_handler(self):
        self.heartbeat.ping_database()
        return "Success", 200

    async def get_same_quote_handler(self):
        return self.quotes.get_same_quote(
            request.args.get("user_id"), request.args.get("quote_id")
        ).__dict__

    async def like_quote_handler(self):
        self.quotes.like_quote(
            request.args.get("user_id"), request.args.get("quote_id")
        )
        return "Success", 200

    async def graphql_explorer(self):
        return self.explorer_html, 200

    async def graphql_query(self):
        data = request.get_json()
        success, result = graphql_sync(
            self.schema,
            data,
            context_value={
                "heartbeat": self.heartbeat,
                "quotes": self.quotes,
            },
        )

        status_code = 200 if success else 400
        return jsonify(result), status_code
