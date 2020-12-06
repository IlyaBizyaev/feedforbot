import asyncio
from asyncio.events import AbstractEventLoop
from typing import List

from yaml import safe_load as yaml_load

from .core import Settings, Listener, Forwarder
from .schemas import ListenerSchema


def read_listeners(path: str):
    listeners = []

    with open(path, 'r') as _f:
        feeds_raw = _f.read()

    listener_schema = ListenerSchema()
    raw_listeners = yaml_load(feeds_raw)

    for raw_listener in raw_listeners:
        raw_listener = listener_schema.dump(raw_listener)

        listener = Listener(url=raw_listener['url'],
                            chat_id=raw_listener['id'],
                            delay=raw_listener['delay'],
                            post_format=raw_listener['format'])

        listeners.append(listener)

    return listeners


class Bot(object):

    def __init__(self,
                 settings: Settings,
                 loop: AbstractEventLoop = None):

        self.settings = settings
        self.loop = loop
        self.listeners: List[Listener] = read_listeners(self.settings.feeds_path)

    def __enter__(self):
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        return self
        # self.loop.set_exception_handler(self.loop_exception_handler)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.close()
        if exc_val:
            raise

    def run(self):
        tasks = list()

        for listener in self.listeners:
            forwarder = Forwarder(tg_token=self.settings.tg_token,
                                  tg_proxy=self.settings.tg_proxy,
                                  listener=listener)

            tasks.append(forwarder.listen())

        self.loop.run_until_complete(asyncio.gather(*tasks))
        self.loop.run_forever()
