class Quote:
    id: str
    quote: str
    author: str
    tags: list[str]
    likes: int

    def __init__(
        self, quote_id: str, quote: str, author: str, tags: list[str], likes: int = 0
    ):
        self.id = quote_id
        self.quote = quote
        self.author = author
        self.tags = tags
        self.likes = likes

    def __eq__(self, other) -> bool:
        return (
            self.id == other.id
            and self.quote == other.quote
            and self.author == other.author
            and self.tags == other.tags
            and self.likes == other.likes
        )


class View:
    quote_id: str
    user_id: str
    liked: bool

    def __init__(self, quote_id: str, user_id: str, liked: bool = False):
        self.quote_id = quote_id
        self.user_id = user_id
        self.liked = liked
