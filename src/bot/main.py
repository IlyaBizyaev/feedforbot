import logging
from typing import Optional

from .bot import Bot
from .core import Settings

DEFAULT_IS_DEBUG = False
DEFAULT_TG_PROXY = None


def main(tg_token: str,
         feeds_path: str,
         is_debug: bool = DEFAULT_IS_DEBUG,
         tg_proxy: Optional[str] = DEFAULT_TG_PROXY) -> None:

    settings = Settings(tg_token=tg_token,
                        is_debug=is_debug,
                        tg_proxy=tg_proxy,
                        feeds_path=feeds_path)

    log_level = logging.DEBUG if settings.is_debug else logging.INFO
    logging.basicConfig(format=settings.log_format,
                        level=log_level)

    with Bot(settings=settings) as bot:
        bot.run()
