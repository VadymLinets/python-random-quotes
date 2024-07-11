import grpc
from fastapi import FastAPI
from flask import Flask
from concurrent import futures
from grpc_reflection.v1alpha import reflection

import src.config.config as cfg
import src.database.sqlalchemy as sqlalchemy
import src.database.peewee as peewee
import src.heartbeat.heartbeat as heartbeat
import src.quote_api.api as api
import src.quote.quote as quote_srv
import src.server.fastapi as fastapi_handlers
import src.server.flask as flask_handlers
import src.grpc.grpc as grpc_server
from src.grpc.proto import quotes_pb2
from src.grpc.proto.quotes_pb2_grpc import add_QuotesServicer_to_server

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
elif server_config.server == "flask":
    app = Flask(__name__)
    h = flask_handlers.Handlers(quotes_service, heartbeat_service)
    app.register_blueprint(h.router)
elif server_config.server == "grpc":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_QuotesServicer_to_server(grpc_server.GRPCServer(quotes_service), server)
    SERVICE_NAMES = (
        quotes_pb2.DESCRIPTOR.services_by_name["Quotes"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port("localhost:{}".format(server_config.grpc_port))
    server.start()
    print("Server started, listening on {}".format(server_config.grpc_port))
    server.wait_for_termination()
else:
    raise Exception("Unknown server")
