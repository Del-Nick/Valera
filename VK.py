import sys

from loguru import logger
from vkbottle.bot import Message

from Admin.Admin import admin_handler
from Config.Config import bot
from Handlers.Event import event_handler
from Handlers.Registration import registration
from Handlers.Settings import settings
from Handlers.StartMenu import start_menu, back_to_start
from Scripts.Arrays import vk_admins
from Server.Core import DB

logger.add("errors.log", format="{time} {level} {message}", level="ERROR")


@bot.on.private_message()
async def message_handler(message: Message):
    user = await DB.select_manager(message)

    if 'Валер' in message.text and 'registration' not in user.action:
        await back_to_start(user, message)

    elif message.text == 'Я админ' and 'registration' not in user.action:
        if user.VkID in vk_admins:
            user.settings.admin = True
            await message.answer('Права предоставлены')

    elif message.text == 'Статистика выборов' and user.settings.studsovet:
        await vote_statistics(user=user, message=message)

    elif message.text == 'DEBUG':
        await message.answer(f'action:  {user.action}')

    else:
        match user.action.split('_')[0]:
            case 'registration':
                await registration(user=user, message=message)

            case 'start':
                await start_menu(user=user, message=message)

            case 'event':
                await event_handler(user=user, message=message)

            case 'settings':
                await settings(user=user, message=message)

            case 'admin':
                await admin_handler(admin=user, message=message)

            case _:
                await back_to_start(user, message)

    await DB.update_user(user)

if __name__ == '__main__':
    bot.run_forever()
