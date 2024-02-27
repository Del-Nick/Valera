from vkbottle.bot import Bot, Message
from vkbottle.tools import PhotoMessageUploader
import asyncio
from Config.Config import token
from loguru import logger
import sys
from Server.DB import User

from Handlers.MainMenu import start_handler
from Handlers.PreStart import *
from Handlers.Settings import settings_handler

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="DEBUG")

bot = Bot(token=token)
uploader = PhotoMessageUploader(bot.api)


@bot.on.private_message()
async def message_handler(message: Message):

    info_vk = await bot.api.users.get(message.from_id)
    info_vk = info_vk[0]
    info_bd = get_all_users_data(info_vk.id)
    settings = get_all_settings(info_vk.id)
    print(message.conversation_message_id)

    answer_is_found = True

    update_all_users_data(info_vk.id, 'num_of_conn', info_bd.num_of_conn + 1)

    if not check_id(info_vk.id):
        await registration(info_vk, message)

    if settings.admin and message.text.lower() == 'отладка':
        answer = f'first_name: {info_bd.first_name}\n' \
                 f'last_name: {info_bd.last_name}\n' \
                 f'sex: {info_bd.sex}\n' \
                    f'action: {info_bd.action}\n' \
                    f'first_conn: {info_bd.first_conn}\n' \
                    f'last_conn: {info_bd.last_conn}\n' \
                    f'num_of_conn: {info_bd.num_of_conn}\n' \
                    f'headman: {info_bd.headman}\n' \
                    f'time_new_schedule: {info_bd.time_new_schedule}\n' \
                    f'group_user: {info_bd.group_user}\n' \
                    f'admin: {info_bd.admin}\n' \
                    f'studsovet: {info_bd.studsovet}\n'
        await message.answer(f'BD_INFO\n\n{answer}')

    elif info_bd.action == 'Add_group':
        await add_user_group(info_vk.id, info_bd, message)

    elif 'Валер' in message.text:
        if info_bd.action == 'Not_student' or info_bd.group_user is None:
            await message.answer(
                'Мои функции доступны только для студентов физического факультета. Если кнопка в начале знакомства '
                'была нажата по ошибке, ты всегда можешь написать "Я студент физфака" или "Я студентка физфака", '
                'чтобы зарегистрироваться')
        else:
            update_all_users_data(info_vk.id, 'action', 'Start')
            await message.answer('Любовь, надежда и вера-а-а', keyboard=standard_keyboard(settings.headman, info_bd))

    elif 'Start' in info_bd.action:
        if await start_handler(info_vk, info_bd, settings, message, uploader) is False:
            answer_is_found = False

    elif 'Settings' in info_bd.action:
        if await settings_handler(info_vk, info_bd, settings, message) is False:
            answer_is_found = False

    if not answer_is_found and len(message.text) < 100:
        last_conn = datetime.datetime.strptime(info_bd.last_conn, '%Y-%m-%d %H:%M:%S.%f')
        if (last_conn - datetime.datetime.now()).total_seconds() < 1:
            if info_bd.action != 'Not_student' or info_bd.group_user is not None:
                await message.answer('Не совсем тебя понял. Тебе нужна моя помощь?',
                                     keyboard=Keyboard(one_time=True)
                                     .add(Text('Валера!'), color=KeyboardButtonColor.POSITIVE).row() \
                                     .add(Text('Нужен человек'), color=KeyboardButtonColor.PRIMARY))
                update_all_users_data(info_vk.id, 'action', 'Start')

bot.run_forever()
