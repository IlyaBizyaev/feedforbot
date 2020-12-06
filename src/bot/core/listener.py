import os
from urllib.parse import quote

import feedparser

from ..models import Feed


def make_filename(chat_id: str, feed_url: str):
    return f"{chat_id}-{quote(feed_url, safe='')}.txt"


class Listener:

    def __init__(self,
                 url: str,
                 chat_id: str,
                 delay: int,
                 post_format: str):

        self.url: str = url
        self.chat_id: str = chat_id
        self.delay: int = delay
        self.post_format: str = post_format.replace('\\n', '\n')

    @property
    def stored_feed(self) -> [str]:
        filename = make_filename(self.chat_id, self.url)

        if not os.path.exists(filename):
            with open(filename, 'w'):
                pass

        with open(filename, 'r') as f:
            stored_urls = [line[:-1] for line in f.readlines()]
        return stored_urls

    def store(self, forwarded_urls: set) -> int:
        filename = make_filename(self.chat_id, self.url)
        with open(filename, 'w') as f:
            f.writelines(line + '\n' for line in forwarded_urls)
        return len(forwarded_urls)

    @property
    def feed(self):
        raw_feed = feedparser.parse(self.url)
        new_feed = Feed()
        new_feed.from_raw(raw_entries=list(raw_feed.entries))

        return new_feed
