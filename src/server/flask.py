from flask import Blueprint, request

from src.quote.quote import Service as quote_srv
from src.heartbeat.heartbeat import Service as heartbeat_srv


class Handlers:
    def __init__(self, quotes: quote_srv, heartbeat: heartbeat_srv):
        self.quotes = quotes
        self.heartbeat = heartbeat

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
