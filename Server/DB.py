import asyncio
import datetime

import asyncpg
from config import user, password, db_name, host, port
import time
import psycopg2


class User:
    def __init__(self, id: int):
        self.id = id
        self.vk_name = None
        self.sex = None
        self.first_conn = None
        self.last_conn = None
        self.group = None
        self.action = None
        self.num_of_conns = None

        self.full_schedule = None
        self.notifications = None
        self.schedule_seller = None
        self.headman = None
        self.studsovet = None
        self.admin = None
        self.time_schedule_seller = None
        self.chatgpt_messages = None

        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.user_info())
        self.loop.run_until_complete(self.settings())

    async def user_info(self):
        conn = await asyncpg.connect(user=user, password=password,
                                     database=db_name, host=host)
        values = await conn.fetch(
            'SELECT * FROM users_new where id = %s', (self.id,),
        )
        await conn.close()
        self.vk_name = values.get('vk_name')
        self.sex = values.get('sex')
        self.first_conn = values.get('first_conn')
        self.last_conn = values.get('last_conn')
        self.group = values.get('user_group')
        self.action = values.get('action')
        self.num_of_conns = values.get('num_of_conns')

    async def settings(self):
        conn = await asyncpg.connect(user=user, password=password,
                                     database=db_name, host=host)
        values = await conn.fetch(
            'SELECT * FROM settings where id = %s', (self.id,),
        )
        await conn.close()
        self.full_schedule = values.get('full_schedule')
        self.notifications = values.get('notifications')
        self.schedule_seller = values.get('schedule_seller')
        self.headman = values.get('headman')
        self.studsovet = values.get('studsovet')
        self.admin = values.get('admin')
        self.time_schedule_seller = values.get('time_schedule_seller')
        self.chatgpt_messages = values.get('chatgpt_messages')