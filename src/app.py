from enum import Enum, auto, unique

from environs import Env
from fire import Fire

from bot.main import main, DEFAULT_IS_DEBUG, DEFAULT_TG_PROXY


@unique
class ConfigurationParameters(Enum):
    ENV_CONFIGURATION = auto()
    FEEDS_PATH = auto()
    TG_PROXY = auto()
    TG_TOKEN = auto()
    IS_DEBUG = auto()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    env_configuration: bool = env.bool(ConfigurationParameters.ENV_CONFIGURATION.name, False)

    if env_configuration:
        tg_token = env(ConfigurationParameters.TG_TOKEN.name)
        feeds_path = env.str(ConfigurationParameters.FEEDS_PATH.name)
        is_debug = env.bool(ConfigurationParameters.IS_DEBUG.name, DEFAULT_IS_DEBUG)
        tg_proxy = env(ConfigurationParameters.TG_PROXY.name, DEFAULT_TG_PROXY)

        main(tg_token=tg_token,
             feeds_path=feeds_path,
             is_debug=is_debug,
             tg_proxy=tg_proxy)

    else:
        Fire(main)
