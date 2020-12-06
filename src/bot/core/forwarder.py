import asyncio
import logging
from dataclasses import asdict
from string import Template
from typing import Optional

from requests import request

from .listener import Listener
from ..models import FeedEntry


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
            logging.debug(f'Check feed {self.listener.url} for user_id {self.listener.chat_id}')

            try:
                await self.check()
            except Exception as err:
                logging.warning(err)
            finally:
                await asyncio.sleep(self.listener.delay)

    async def check(self):
        forwarded_urls = set(self.listener.stored_feed)
        feed = self.listener.feed

        new_messages_cnt = 0
        forwarded_cnt = 0

        if not feed.entries:
            logging.info(f'Got empty feed from "{self.listener.url}"')
        else:
            for entry in feed.entries:
                if entry.url not in forwarded_urls:
                    new_messages_cnt += 1
                    result = self.send_entry(entry)
                    if result:
                        forwarded_cnt += 1

            if new_messages_cnt:
                new_urls = [entry.url for entry in feed.entries]
                forwarded_urls.update(new_urls)
                self.listener.store(forwarded_urls)
                msg = f'Received {new_messages_cnt} new messages from {self.listener.url}, forwarded {forwarded_cnt}'
            else:
                msg = f'No new messages from {self.listener.url}, nothing to do'
            logging.info(msg)
