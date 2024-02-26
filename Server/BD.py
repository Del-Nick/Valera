import asyncio
import asyncpg
from config import user, password, db_name, host, port
import time
import psycopg2


async def run():
    conn = await asyncpg.connect(user=user, password=password,
                                 database=db_name, host=host)
    values = await conn.fetch(
        'SELECT * FROM users',
    )
    await conn.close()


def old():
    conn = psycopg2.connect(user=user,
                            password=password,
                            host=host,
                            port=port,
                            database=db_name)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    values = cursor.fetchall()

    cursor.close()
    conn.close()


num = 1000

timer = time.time()
for t in range(num):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

print((time.time()-timer)/num)

timer = time.time()
for t in range(num):
    old()

print((time.time()-timer)/num)