import asyncio
import time

from Config.Config import bot, uploader
from Server.DB import User
from Handlers.Registration import registration
from Handlers.StartMenu import start_menu, back_to_start
from Handlers.Settings import settings
from Scripts.Arrays import vk_admins

from vkbottle.bot import Bot, Message

from loguru import logger
import sys

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="DEBUG")


@bot.on.private_message()
async def message_handler(message: Message):

    # Получение информации о пользователе из вк
    vk_info = (await bot.api.users.get(message.from_id))[0]

    # Собираем всю информацию о пользователе из базы данных
    user = User(vk=vk_info, message=message, vk_id=message.from_id)
    await user.connection()

    if 'Валер' in message.text:
        await back_to_start(user, message)

    elif message.text == 'Я админ':
        if user.vk_id in vk_admins:
            user.admin = True
            await user.update()
            await message.answer('Права предоставлены')

    elif message.text == 'DEBUG':
        await message.answer(f'action:  {user.action}')

    else:
        match user.action.split('_')[0]:

            case 'registration':
                await registration(user=user, message=message)

            case 'start':
                await start_menu(user=user, message=message)

            case 'settings':
                await settings(user=user, message=message)

            case _:
                await back_to_start(user, message)


    await user.update()





bot.run_forever()
