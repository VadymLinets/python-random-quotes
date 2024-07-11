import logging
from grpc_status import rpc_status
from google.rpc import status_pb2
from google.rpc import code_pb2

from src.grpc.proto.quotes_pb2 import Quote, Empty
from src.grpc.proto.quotes_pb2_grpc import QuotesServicer
from src.quote.quote import Service as QuoteService


class GRPCServer(QuotesServicer):
    def __init__(self, quotes: QuoteService):
        self.quotes = quotes

    def GetQuoteHandler(self, request, context):
        try:
            quote = self.quotes.get_quote(request.user_id)
            return Quote(
                id=quote.id,
                quote=quote.quote,
                author=quote.author,
                tags=quote.tags,
                likes=quote.likes,
            )
        except Exception as e:
            logging.error("Failed to get quote", exc_info=e)
            context.abort_with_status(self.__internal_error("Failed to get quote"))

    def GetSameQuoteHandler(self, request, context):
        try:
            quote = self.quotes.get_same_quote(request.user_id, request.quote_id)
            return Quote(
                id=quote.id,
                quote=quote.quote,
                author=quote.author,
                tags=quote.tags,
                likes=quote.likes,
            )
        except Exception as e:
            logging.error("Failed to get same quote", exc_info=e)
            context.abort_with_status(self.__internal_error("Failed to get same quote"))

    def LikeQuoteHandler(self, request, context):
        try:
            self.quotes.like_quote(request.user_id, request.quote_id)
            return Empty()
        except Exception as e:
            logging.error("Failed to like quote", exc_info=e)
            context.abort_with_status(self.__internal_error("Failed to like quote"))

    @staticmethod
    def __internal_error(msg: str):
        return rpc_status.to_status(
            status_pb2.Status(
                code=code_pb2.INTERNAL,
                message=msg,
            )
        )
