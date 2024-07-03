from fastapi import FastAPI
from flask import Flask
import src.config.config as cfg
import src.database.sqlalchemy as sqlalchemy
import src.database.peewee as peewee
import src.heartbeat.heartbeat as heartbeat
import src.quote_api.api as api
import src.quote.quote as quote_srv
import src.server.fastapi as fastapi_handlers
import src.server.flask as flask_handlers

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
else:
    raise Exception("Unknown server")
