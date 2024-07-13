import grpc
from ariadne.explorer import ExplorerGraphiQL
from fastapi import FastAPI
from flask import Flask
from litestar import Litestar
from concurrent import futures
from grpc_reflection.v1alpha import reflection
from litestar.di import Provide
from starlette.applications import Starlette

import src.config.config as cfg
import src.database.sqlalchemy as sqlalchemy
import src.database.peewee as peewee
import src.heartbeat.heartbeat as heartbeat
import src.quote_api.api as api
import src.quote.quote as quote_srv
import src.server.fastapi as fastapi_handlers
import src.server.flask as flask_handlers
import src.server.litestar as litestar_handlers
import src.server.starlette as starlette_handlers
import src.server.grpc as grpc_server
from src.server.graphql.schema import get_schema
from src.server.proto import quotes_pb2
from src.server.proto.quotes_pb2_grpc import add_QuotesServicer_to_server

postgres_config = cfg.PostgresConfig()
if postgres_config.orm == "sqlalchemy":
    db = sqlalchemy.Postgres(postgres_config)
elif postgres_config.orm == "peewee":
    db = peewee.Postgres(postgres_config)
else:
    raise Exception("Unknown orm")

quote_api = api.Service(db)
quotes_service = quote_srv.Service(cfg.QuotesConfig(), db, quote_api)
heartbeat_service = heartbeat.Service(db)

server_config = cfg.ServerConfig()
if server_config.server == "fastapi":
    app = FastAPI()
    h = fastapi_handlers.Handlers(quotes_service, heartbeat_service)
    app.include_router(h.router)
elif server_config.server == "litestar":

    def wrapper(service):
        async def f():
            return service

        return f

    app = Litestar(
        route_handlers=[litestar_handlers.Handlers],
        dependencies={
            "quotes": Provide(wrapper(quotes_service)),
            "heartbeat": Provide(wrapper(heartbeat_service)),
            "graphql_schema": Provide(wrapper(get_schema())),
            "explorer_html": Provide(wrapper(ExplorerGraphiQL().html(None))),
        },
    )
elif server_config.server == "flask":
    app = Flask(__name__)
    h = flask_handlers.Handlers(quotes_service, heartbeat_service)
    app.register_blueprint(h.router)
elif server_config.server == "starlette":
    h = starlette_handlers.Handlers(quotes_service, heartbeat_service)
    app = Starlette(routes=h.routes)
elif server_config.server == "grpc":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    quotes = grpc_server.GRPCServer(quotes_service, heartbeat_service)
    add_QuotesServicer_to_server(quotes, server)
    SERVICE_NAMES = (
        quotes_pb2.DESCRIPTOR.services_by_name["Quotes"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port("localhost:{}".format(server_config.grpc_port))
    try:
        server.start()
        print("Server started, listening on {}".format(server_config.grpc_port))
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
        print("Server disconnected")
else:
    raise Exception("Unknown server")
