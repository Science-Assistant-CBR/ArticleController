from environs import Env
from dataclasses import dataclass


@dataclass
class Bots:
    bot_token: str
    timedelta: int
    yadisk_token: str
    digest_directory: str


@dataclass
class Settings:
    bots: Bots


def get_settings(path: str):
    env = Env()
    env.read_env(path)

    return Settings(
        bots=Bots(
            bot_token=env.str("TOKEN"),
            timedelta = env.int("TIMEDELTA"),
            yadisk_token = env.str("YANDEX_TOKEN"),
            digest_directory=env.str("DIGEST_DIRECTORY")
        )
    )


settings = get_settings("input.env")