import asyncio
import datetime
import time

import asyncpg
from vkbottle.bot import Bot, Message
from vkbottle_types.codegen.objects import UsersUserFull

from Config.Config import user, password, db_name, host, port


class User:
    def __init__(self,
                 vk: UsersUserFull = None,
                 message: Message = None,
                 vk_id: int | None = None,
                 telegram_id: int | None = None):

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
        self.schedule_next_day_after = None
        self.chatgpt_messages = None

        self.message = message
        self.vk = vk

        self.conn = None

    async def connection(self):
        self.conn = await asyncpg.connect(user=user, password=password,
                                          database=db_name, host=host)
        await self.user_info()
        await self.settings()

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
            await self.add_new_user()
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
            self.schedule_next_day_after = values.get('schedule_next_day_after')
            self.chatgpt_messages = values.get('chatgpt_messages')

    async def add_new_user(self):
        print('Регистрирую нового пользователя')
        self.action = 'registration_first_message'

        if self.vk_id:
            self.vk_name = f'{self.vk.first_name} {self.vk.last_name}'

        print(self.vk_name)

        if self.vk_id is not None or self.telegram_id is not None:
            async with self.conn.transaction():
                await self.conn.execute('INSERT INTO users_new '
                                        '(vk_id, vk_name, first_conn, last_conn, user_group, '
                                        'action, num_of_conns, telegram_id, telegram_name) '
                                        'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)',
                                        self.vk_id,
                                        f'{self.vk.first_name} {self.vk.last_name}',
                                        datetime.datetime.now(),
                                        datetime.datetime.now(),
                                        self.group,
                                        self.action,
                                        1,
                                        self.telegram_id,
                                        self.telegram_name)

        if self.vk_id is not None or self.telegram_id is not None:
            async with self.conn.transaction():
                await self.conn.execute('INSERT INTO settings '
                                        '(vk_id, vk_name, telegram_id, telegram_name, full_schedule, notifications, '
                                        'schedule_seller, headman, studsovet, admin, schedule_next_day_after, '
                                        'chatgpt_messages) '
                                        'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)',
                                        self.vk_id,
                                        self.vk_name,
                                        self.telegram_id,
                                        self.telegram_name,
                                        False,
                                        False,
                                        False,
                                        False,
                                        False,
                                        False,
                                        '18:00',
                                        '[]')

    async def update(self):
        await self.update_user_info()
        await self.update_settings()

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
                                        self.num_of_conns + 1)

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

    async def delete_row(self):
        if self.admin:
            async with self.conn.transaction():
                if self.vk_id is not None:
                    await self.conn.execute('''DELETE FROM users_new WHERE vk_id = $1''', self.vk_id)
                elif self.telegram_id is not None:
                    await self.conn.execute('''DELETE FROM users_new WHERE telegram_id = $1''', self.telegram_id)

            async with self.conn.transaction():
                if self.vk_id is not None:
                    await self.conn.execute('''DELETE FROM settings WHERE vk_id = $1''', self.vk_id)
                elif self.telegram_id is not None:
                    await self.conn.execute('''DELETE FROM settings WHERE telegram_id = $1''', self.telegram_id)