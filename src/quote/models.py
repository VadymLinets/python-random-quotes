from pydantic import BaseModel


class Quote(BaseModel):
    id: str
    quote: str
    author: str
    tags: list[str]
    likes: int = 0

    def __eq__(self, other) -> bool:
        return (
            self.id == other.id
            and self.quote == other.quote
            and self.author == other.author
            and self.tags == other.tags
            and self.likes == other.likes
        )


class View(BaseModel):
    quote_id: str
    user_id: str
    liked: bool = False
