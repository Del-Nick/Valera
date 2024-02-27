import asyncio
import datetime

import asyncpg

from Config.Config import user, password, db_name, host


async def users():
    conn = await asyncpg.connect(user=user, password=password,
                                 database=db_name, host=host)
    values = await conn.fetch(
        'SELECT * FROM users',
    )

    for value in values:
        if type(value.get('group_user')) is str:
            group = value.get('group_user').replace(' ', '')
        else:
            group = value.get('group_user')
        await conn.execute('INSERT INTO users_new '
                           '(id, vk_name, sex, first_conn, last_conn, user_group, action, num_of_conns) '
                           'VALUES'
                           '($1, $2, $3, $4, $5, $6, $7, $8)',
                           value.get('id'),
                           f'{value.get("first_name")} {value.get("last_name")}',
                           value.get('sex'),
                           datetime.datetime.strptime(value.get('first_conn'), '%Y-%m-%d %H:%M:%S.%f'),
                           datetime.datetime.strptime(value.get('last_conn'), '%Y-%m-%d %H:%M:%S.%f'),
                           group,
                           value.get('action'),
                           value.get('num_of_conn'),)
    await conn.close()


async def settings():
    conn = await asyncpg.connect(user=user, password=password,
                                 database=db_name, host=host)
    values = await conn.fetch(
        'SELECT * FROM users',
    )

    for value in values:
        async with conn.transaction():
            await conn.execute('INSERT INTO settings '
                               '(vk_id, '
                               'vk_name, '
                               'full_schedule, '
                               'notifications, '
                               'schedule_seller, '
                               'headman, '
                               'studsovet, '
                               'admin, '
                               'schedule_next_day_after, '
                               'chatgpt_messages) '
                               'VALUES'
                               '($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)',
                               value.get('id'),
                               f'{value.get("first_name")} {value.get("last_name")}',
                               False,
                               False,
                               False,
                               value.get('headman'),
                               value.get('studsovet'),
                               value.get('admin'),
                               value.get('time_new_schedule'),
                               '[]')
    await conn.close()


loop = asyncio.get_event_loop()
# loop.run_until_complete(user())
loop.run_until_complete(settings())