from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session
from sqlalchemy import ForeignKey
from sqlalchemy import Column
from sqlalchemy import TEXT
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import case
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.types import ARRAY

from src.config.config import PostgresConfig
from src.quote.interfaces import DBInterface as quote_db
from src.quote_api.interfaces import DBInterface as quote_api_db
from src.heartbeat.interfaces import DBInterface as heartbeat_db


class Base(DeclarativeBase):
    pass


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(primary_key=True)
    quote: Mapped[str]
    author: Mapped[str]
    tags = Column(ARRAY(TEXT))
    likes: Mapped[int]

    def __repr__(self) -> str:
        return f"Quote(id={self.id!r}, quote={self.quote!r}, author={self.author!r}, tags={self.tags!r}, likes={self.likes!r})"


class View(Base):
    __tablename__ = "views"

    quote_id: Mapped[str] = mapped_column(ForeignKey("quotes.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(primary_key=True)
    liked: Mapped[bool]

    def __repr__(self) -> str:
        return f"View(quote_id={self.quote_id!r}, user_id={self.user_id!r}, liked={self.liked!r})"


class Postgres(quote_db, quote_api_db, heartbeat_db):
    def __init__(self, cfg: PostgresConfig):
        self.engine = create_engine(cfg.dsn)

    def ping(self) -> None:
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    def get_quote(self, quote_id: str) -> Quote:
        with Session(self.engine) as session:
            return session.scalar(select(Quote).where(Quote.id == quote_id))

    def get_quotes(self, user_id: str) -> list[Quote]:
        with Session(self.engine) as session:
            return session.scalars(
                select(Quote).where(
                    Quote.id.not_in(
                        select(View.quote_id).where(View.user_id == user_id)
                    )
                )
            ).all()

    def get_same_quote(self, user_id: str, viewed_quote: Quote) -> Quote:
        tags = "'" + "', '".join(viewed_quote.tags) + "'"
        with Session(self.engine) as session:
            return session.scalars(
                select(Quote)
                .where(
                    Quote.id.not_in(
                        select(View.quote_id).where(View.user_id == user_id)
                    )
                )
                .order_by(
                    text(
                        "cardinality(array(select unnest(quotes.tags) intersect select unnest(array["
                        + tags
                        + "]))) DESC"
                    )
                )
                .order_by(case((Quote.author == viewed_quote.author, 1), else_=2))
                .order_by(Quote.likes.desc())
                .limit(1)
            ).first()

    def get_view(self, quote_id: str, user_id: str) -> View:
        with Session(self.engine) as session:
            return session.scalar(
                select(View).where(View.user_id == user_id, View.quote_id == quote_id)
            )

    def save_quote(self, quote: Quote) -> None:
        with Session(self.engine) as session:
            session.execute(
                insert(Quote)
                .values(
                    id=quote.id,
                    quote=quote.quote,
                    author=quote.author,
                    tags=quote.tags,
                    likes=quote.likes,
                )
                .on_conflict_do_nothing()
            )
            session.commit()

    def mark_as_viewed(self, quote_id: str, user_id: str) -> None:
        with Session(self.engine) as session:
            session.execute(
                insert(View)
                .values(
                    user_id=user_id,
                    quote_id=quote_id,
                    liked=False,
                )
                .on_conflict_do_nothing()
            )
            session.commit()

    def mark_as_liked(self, quote_id: str, user_id: str) -> None:
        with Session(self.engine) as session:
            session.query(View).filter(
                View.user_id == user_id,
                View.quote_id == quote_id,
            ).update({View.liked: True})
            session.commit()

    def like_quote(self, quote_id: str) -> None:
        with Session(self.engine) as session:
            session.query(Quote).filter(Quote.id == quote_id).update(
                {Quote.likes: Quote.likes + 1}
            )
            session.commit()
