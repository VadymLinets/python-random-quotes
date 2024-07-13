from flask import Blueprint, request, jsonify
from ariadne import graphql_sync
from ariadne.explorer import ExplorerGraphiQL

from src.quote.quote import Service as QuoteService
from src.heartbeat.heartbeat import Service as HeartbeatService
from src.server.graphql.schema import get_schema


class Handlers:
    def __init__(self, quotes: QuoteService, heartbeat: HeartbeatService):
        self.quotes = quotes
        self.heartbeat = heartbeat
        self.schema = get_schema()
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
