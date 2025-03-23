import asyncio
from dataclasses import dataclass

from dotenv import find_dotenv, load_dotenv, dotenv_values
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.testing.plugin.plugin_base import config
from vkbottle import API
from vkbottle.bot import Bot
from vkbottle.tools import PhotoMessageUploader, DocMessagesUploader

# load_dotenv(find_dotenv(".env"))
load_dotenv('Config/.env')


@dataclass
class GlobalSettings:
    config = dotenv_values()
    print(f'{config = }')

    host: str = config['host']
    user: str = config['user']
    password: str = config['password']
    db_name: str = config['db_name']
    port: int = config['port']

    vk_ss_ff_token: str = config['vk_ss_ff_token']
    # vk_main_token: str = config['vk_main_token']

    # main_token: str = config['tg_main_token']
    owner_id: str = config['owner_id']

    # ssh_host: str = config['ssh_host']
    # ssh_username: str = config['ssh_username']
    # ssh_password: str = config['ssh_password']
    # ssh_port: int = config['ssh_port']

    admins = tuple(map(int, config['tg_admins'].split()))

    def __init__(self):
        self.engine = create_async_engine(url=self.DATABASE_URL_asyncpg,
                                          echo=False)
        self.session_factory = async_sessionmaker(self.engine)
        print(self.DATABASE_URL_asyncpg)

    @property
    def DATABASE_URL_asyncpg(self):
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


global_settings = GlobalSettings()

MAIN_GROUP = False
GETTING_ERROR = True

if MAIN_GROUP:
    api = API(token=global_settings.vk_main_token)
    bot = Bot(token=global_settings.vk_main_token)
    photo_uploader = PhotoMessageUploader(bot.api)
    doc_uploader = DocMessagesUploader(bot.api)

else:
    api = API(token=global_settings.vk_ss_ff_token)
    bot = Bot(token=global_settings.vk_ss_ff_token)
    photo_uploader = PhotoMessageUploader(bot.api)
    doc_uploader = DocMessagesUploader(bot.api)
