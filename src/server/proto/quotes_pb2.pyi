from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UserIDRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class UserAndQuoteIDRequest(_message.Message):
    __slots__ = ("user_id", "quote_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTE_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    quote_id: str
    def __init__(
        self, user_id: _Optional[str] = ..., quote_id: _Optional[str] = ...
    ) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Quote(_message.Message):
    __slots__ = ("id", "quote", "author", "tags", "likes")
    ID_FIELD_NUMBER: _ClassVar[int]
    QUOTE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    LIKES_FIELD_NUMBER: _ClassVar[int]
    id: str
    quote: str
    author: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    likes: int
    def __init__(
        self,
        id: _Optional[str] = ...,
        quote: _Optional[str] = ...,
        author: _Optional[str] = ...,
        tags: _Optional[_Iterable[str]] = ...,
        likes: _Optional[int] = ...,
    ) -> None: ...
