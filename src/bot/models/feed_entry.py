from dataclasses import dataclass
from html import escape


@dataclass
class FeedEntry:
    published: str
    title: str
    url: str
    author: str

    forwarded: bool = False

    def __post_init__(self):
        self.author = escape(self.author) if self.author else None
        # TODO rewrite from str to datetime type
        self.published = escape(self.published) if self.published else None
        self.title = escape(self.title) if self.title else None
        self.url = escape(self.url) if self.url else None
