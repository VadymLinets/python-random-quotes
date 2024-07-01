from fastapi import FastAPI
import src.config.config as cfg
import src.database.sqlalchemy as sql
# import src.database.peewee as sql
import src.heartbeat.heartbeat as heartbeat
import src.quote_api.api as api
import src.quote.quote as quote_srv
import src.server.fastapi as handlers


db = sql.Postgres(cfg.PostgresConfig())
quote_api = api.Service(db)
quotes_service = quote_srv.Service(cfg.QuotesConfig(), db, quote_api)
heartbeat_service = heartbeat.Service(db)

app = FastAPI()
h = handlers.Handlers(quotes_service, heartbeat_service)
app.include_router(h.router)
