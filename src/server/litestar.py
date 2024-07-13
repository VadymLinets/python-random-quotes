import logging
from http import HTTPStatus
from ariadne import graphql
from graphql import GraphQLSchema
from litestar import get, patch, Controller, Request, post, MediaType, Response
from litestar.exceptions import HTTPException

from src.quote.quote import Service as QuoteService, Quote
from src.heartbeat.heartbeat import Service as HeartbeatService


class Handlers(Controller):
    path = "/"

    @get("/")
    async def get_quote_handler(self, quotes: QuoteService, user_id: str) -> Quote:
        try:
            return quotes.get_quote(user_id)
        except Exception as e:
            logging.error("Failed to get quote", exc_info=e)
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    @get("/heartbeat")
    async def heartbeat_handler(self, heartbeat: HeartbeatService) -> None:
        try:
            return heartbeat.ping_database()
        except Exception as e:
            logging.error("Failed to get quote", exc_info=e)
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    @get("/same")
    async def get_same_quote_handler(
        self, quotes: QuoteService, user_id: str, quote_id: str
    ) -> Quote:
        try:
            return quotes.get_same_quote(user_id, quote_id)
        except Exception as e:
            logging.error("Failed to get quote", exc_info=e)
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    @patch("/like")
    async def like_quote_handler(
        self, quotes: QuoteService, user_id: str, quote_id: str
    ) -> None:
        try:
            return quotes.like_quote(user_id, quote_id)
        except Exception as e:
            logging.error("Failed to get quote", exc_info=e)
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    @get("/graphql")
    async def graphql_explorer(self, explorer_html: str) -> str:
        return explorer_html

    @post("/graphql")
    async def graphql_query(
        self,
        graphql_schema: GraphQLSchema,
        quotes: QuoteService,
        heartbeat: HeartbeatService,
        request: Request,
    ) -> Response[dict]:
        data = await request.json()
        success, result = await graphql(
            graphql_schema,
            data,
            context_value={
                "heartbeat": heartbeat,
                "quotes": quotes,
            },
        )

        status_code = 200 if success else 400
        return Response(
            status_code=status_code, content=result, media_type=MediaType.JSON
        )
