import asyncio
import logging
from dataclasses import asdict
from string import Template
from typing import Optional

from requests import request
from urllib.parse import urlparse

from .listener import Listener
from ..models import FeedEntry


MAX_CACHED_URLS = 1000
WWW_PREFIX = 'www.'
COMMON_SUFFIXES = ['htm', 'html']


def normalize_url(url_str: str) -> str:
    url = urlparse(url_str)
    post_part = url.path.rstrip('/').lstrip('/')
    # Some blogs use queries as post addresses.
    if not post_part and url.query:
        post_part = '?' + url.query
    # This intentionally does not include the scheme.
    result = url.netloc + '/' + post_part
    # Drop some other common bits.
    if result.startswith(WWW_PREFIX):
        result = result[len(WWW_PREFIX):]
    ext_split = result.rsplit('.', 1)
    if ext_split[1] in COMMON_SUFFIXES:
        result = ext_split[0]
    return result


class Forwarder:
    def __init__(self,
                 tg_token: str,
                 tg_proxy: Optional[str],
                 listener: Listener):

        self.tg_token = tg_token
        self.tg_proxy = tg_proxy
        self.listener = listener

    def send_telegram_message(self, text: str):
        url = f'https://api.telegram.org/bot{self.tg_token}/sendMessage'
        data = dict(chat_id=self.listener.chat_id,
                    text=text,
                    parse_mode='HTML')
        # todo check invalid token
        try:
            response = request(method='POST',
                               url=url,
                               data=data,
                               proxies=dict(https=self.tg_proxy))
            return response
        except Exception as err:
            logging.warning(err)

    def send_entry(self, entry: FeedEntry):
        template_dict = asdict(entry)
        output = Template(self.listener.post_format).safe_substitute(template_dict)
        logging.debug(f'Send to "{self.listener.chat_id}": "{output}"')
        # preview = not self.listener.preview
        # self.src.sendMessage(self.userId, output, parse_mode='HTML',
        #                      disable_web_page_preview=preview)
        response = self.send_telegram_message(output)

        return response and response.ok

    async def listen(self):
        while True:
            logging.debug(f'Check feed {self.listener.url} for chat_id {self.listener.chat_id}')

            try:
                await self.check()
            except Exception as err:
                logging.warning(err)
            finally:
                await asyncio.sleep(self.listener.delay)

    async def check(self):
        loaded_feed = self.listener.feed

        if not loaded_feed.entries:
            logging.info(f'Got empty feed from "{self.listener.url}"')
        else:
            stored_urls = self.listener.stored_feed
            stored_urls_set = set(stored_urls)

            new_urls = []
            failed_urls = []

            for entry in loaded_feed.entries:
                normalized_entry_url = normalize_url(entry.url)
                if normalized_entry_url not in stored_urls_set:
                    new_urls.append(normalized_entry_url)
                    if not self.send_entry(entry):
                        failed_urls.append(normalized_entry_url)

            if not new_urls:
                msg = f'No new messages from {self.listener.url}, nothing to do'
            else:
                self.listener.store((stored_urls + new_urls)[-MAX_CACHED_URLS:])
                msg = f'Received {len(new_urls)} new entries from {self.listener.url}, '
                if failed_urls:
                    msg += f'failed to forward: {failed_urls}.'
                else:
                    msg += 'forwarded all.'

            logging.info(msg)
