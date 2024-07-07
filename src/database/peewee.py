from peewee import (
    DatabaseProxy,
    Model,
    TextField,
    IntegerField,
    BooleanField,
    CompositeKey,
    SQL,
    Case,
    DoesNotExist,
)
import playhouse.postgres_ext as pg
from playhouse.db_url import connect

from src.config.config import PostgresConfig
from src.quote.interfaces import DBInterface as quote_db
from src.quote_api.interfaces import DBInterface as quote_api_db
from src.heartbeat.interfaces import DBInterface as heartbeat_db

db = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = db


class Quote(BaseModel):
    id = TextField(primary_key=True)
    quote = TextField()
    author = TextField()
    tags = pg.ArrayField(pg.TextField)
    likes = IntegerField()

    class Meta:
        table_name = "quotes"


class View(BaseModel):
    user_id = TextField()
    quote_id = TextField()
    liked = BooleanField()

    class Meta:
        table_name = "views"
        primary_key = CompositeKey("user_id", "quote_id")


class Postgres(quote_db, quote_api_db, heartbeat_db):
    def __init__(self, cfg: PostgresConfig):
        db.initialize(connect(cfg.dsn))

    def ping(self) -> None:
        db.execute_sql("select 1")

    def get_quote(self, quote_id: str) -> Quote:
        return Quote.get_by_id(quote_id)

    def get_quotes(self, user_id: str) -> list[Quote]:
        return Quote.select().where(
            Quote.id.not_in(View.select(View.quote_id).where(View.user_id == user_id))
        )

    def get_same_quote(self, user_id: str, viewed_quote: Quote) -> Quote | None:
        tags = "'" + "', '".join(viewed_quote.tags) + "'"
        try:
            return (
                Quote.select()
                .where(
                    Quote.id.not_in(
                        View.select(View.quote_id).where(View.user_id == user_id)
                    )
                )
                .order_by(
                    SQL(
                        "cardinality(array(select unnest(tags) intersect select unnest(array["
                        + tags
                        + "])))"
                    ).desc(),
                    Case(None, [((Quote.author == viewed_quote.author), 1)], 2),
                    Quote.likes.desc(),
                )
                .limit(1)
                .get()
            )
        except DoesNotExist:
            return None

    def get_view(self, quote_id: str, user_id: str) -> View | None:
        return View.get_by_id((user_id, quote_id))

    def save_quote(self, quote: Quote) -> None:
        Quote.insert(
            id=quote.id,
            quote=quote.quote,
            author=quote.author,
            tags=quote.tags,
            likes=quote.likes,
        ).on_conflict_ignore().execute()

    def mark_as_viewed(self, quote_id: str, user_id: str) -> None:
        View.insert(
            user_id=user_id, quote_id=quote_id, liked=False
        ).on_conflict_ignore().execute()

    def mark_as_liked(self, quote_id: str, user_id: str) -> None:
        View.update(liked=True).where(
            View.user_id == user_id, View.quote_id == quote_id
        ).execute()

    def like_quote(self, quote_id: str) -> None:
        Quote.update(likes=Quote.likes + 1).where(Quote.id == quote_id).execute()
