import asyncio

import asyncpg
import vkbottle

from Config.Config import user, password, db_name, host, port


async def connection():
    return await asyncpg.connect(user=user, password=password,
                                 database=db_name, host=host)


class User:
    def __init__(self, message, vk_id: int | None = None, telegram_id: int | None = None):
        self.vk_id = vk_id
        self.vk_name = None
        self.telegram_id = telegram_id
        self.telegram_name = None
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

        self.message = message

        self.loop = asyncio.get_event_loop()
        self.conn = self.loop.run_until_complete(connection())

        self.loop.run_until_complete(self.user_info())
        self.loop.run_until_complete(self.settings())

    async def user_info(self):
        if self.vk_id is not None:
            values = await self.conn.fetch(
                'SELECT * FROM users_new where vk_id = $1', self.vk_id,
            )
        elif self.telegram_id is not None:
            values = await self.conn.fetch(
                'SELECT * FROM users_new where telegram_id = $1', self.telegram_id,
            )
        else:
            return None

        if not values:
            self.loop.run_until_complete(self.add_new_user())
        else:
            values = values[0]

            self.vk_name = values.get('vk_name')
            self.telegram_name = values.get('telegram_name')
            self.sex = values.get('sex')
            self.first_conn = values.get('first_conn')
            self.last_conn = values.get('last_conn')
            self.group = values.get('user_group')
            self.action = values.get('action')
            self.num_of_conns = values.get('num_of_conns')

    async def settings(self):
        if self.vk_id is not None:
            values = await self.conn.fetch(
                'SELECT * FROM settings where vk_id = $1', self.vk_id,
            )
        elif self.telegram_id is not None:
            values = await self.conn.fetch(
                'SELECT * FROM settings where telegram_id = $1', self.telegram_id,
            )
        else:
            return None

        if values:
            values = values[0]

            self.full_schedule = values.get('full_schedule')
            self.notifications = values.get('notifications')
            self.schedule_seller = values.get('schedule_seller')
            self.headman = values.get('headman')
            self.studsovet = values.get('studsovet')
            self.admin = values.get('admin')
            self.time_schedule_seller = values.get('time_schedule_seller')
            self.chatgpt_messages = values.get('chatgpt_messages')

    async def add_new_user(self):
        async with self.conn.transaction():
            if self.vk_id is not None:
                await self.conn.execute('INSERT INTO settings '
                                        '(vk_id, vk_name, full_schedule, notifications, schedule_seller, '
                                        'headman, studsovet, admin, schedule_next_day_after, chatgpt_messages) '
                                        'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
                                        self.vk_id,
                                        f'{self.message.first_name} {self.message.last_name}',
                                        False,
                                        False,
                                        False,
                                        False,
                                        False,
                                        False,
                                        '18:00',
                                        '[]')
            elif self.telegram_id is not None:
                await self.conn.execute('INSERT INTO settings '
                                        '(telegram_id, vk_name, full_schedule, notifications, schedule_seller, '
                                        'headman, studsovet, admin, schedule_next_day_after, chatgpt_messages) '
                                        'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
                                        self.telegram_id,
                                        f'{self.message.first_name} {self.message.last_name}',
                                        False,
                                        False,
                                        False,
                                        False,
                                        False,
                                        False,
                                        '18:00',
                                        '[]')

    def update(self):
        self.loop.run_until_complete(self.update_user_info())
        self.loop.run_until_complete(self.update_settings())

    async def update_user_info(self):
        async with self.conn.transaction():
            if self.vk_id is not None:
                await self.conn.execute('''
                            UPDATE users_new 
                            SET (last_conn, user_group, action, num_of_conns)=
                            ($2, $3, $4, $5) 
                            WHERE vk_id=$1''',
                                        self.vk_id,
                                        self.last_conn,
                                        self.group,
                                        self.action,
                                        self.num_of_conns)
            elif self.telegram_id is not None:
                await self.conn.execute('''
                            UPDATE users_new 
                            SET (last_conn, user_group, action, num_of_conns)=
                            ($2, $3, $4, $5) 
                            WHERE telegram_id=$1''',
                                        self.telegram_id,
                                        self.last_conn,
                                        self.group,
                                        self.action,
                                        self.num_of_conns)

    async def update_settings(self):
        async with self.conn.transaction():
            if self.vk_id is not None:
                await self.conn.execute('''
                            UPDATE settings 
                            SET (full_schedule, notifications, schedule_seller, headman, 
                            studsovet, admin, time_schedule_seller, chatgpt_messages)=
                            ($2, $3, $4, $5, $6, $7, $8, $9) 
                            WHERE vk_id=$1''',
                                        self.vk_id,
                                        self.full_schedule,
                                        self.notifications,
                                        self.schedule_seller,
                                        self.headman,
                                        self.studsovet,
                                        self.admin,
                                        self.time_schedule_seller,
                                        self.chatgpt_messages, )
            elif self.telegram_id is not None:
                await self.conn.execute('''
                            UPDATE settings 
                            SET (full_schedule, notifications, schedule_seller, headman, 
                            studsovet, admin, time_schedule_seller, chatgpt_messages)=
                            ($2, $3, $4, $5, $6, $7, $8, $9) 
                            WHERE telegram_id=$1''',
                                        self.telegram_id,
                                        self.full_schedule,
                                        self.notifications,
                                        self.schedule_seller,
                                        self.headman,
                                        self.studsovet,
                                        self.admin,
                                        self.time_schedule_seller,
                                        self.chatgpt_messages, )
