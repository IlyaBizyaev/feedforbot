from typing import List, Dict

from .feed_entry import FeedEntry


class Feed:

    def __init__(self):
        self.entries: List[FeedEntry] = list()

    def from_raw(self, raw_entries: List[Dict]):

        for raw_entry in raw_entries:
            entry = FeedEntry(published=raw_entry.get('published'),
                              title=raw_entry.get('title'),
                              url=raw_entry.get('link') if 'link' in raw_entry else raw_entry.get('id'),
                              author=raw_entry.get('author'))

            self.entries.append(entry)

        self.entries.reverse()

        return self.entries
