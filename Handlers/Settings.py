import difflib
import re

from vkbottle.bot import Message
from Server.DB import User
from Handlers.Keyboards import *
from Scripts.Arrays import groups


async def start_settings(user: User, message: Message):
    await message.answer(f'VK ID: {user.vk_id}')
    answer = f'Группа:  {user.group.split(",")[0]}\n'

    if len(user.group.split(",")) > 1:
        groups = ', '.join(user.group.split(",")[1:])
    else:
        groups = 'Нет'

    answer += f'Доп. группы:  {groups}\n'
    answer += f'Расписание на следующий день после {user.schedule_next_day_after}'
    await message.answer(answer,
                         keyboard=settings_keyboard(user))

async def settings(user: User, message: Message):
    match user.action.replace('settings_', ''):

        case 'main':
            if 'Время' in message.text:
                user.action = 'settings_get_schedule_time'
                await message.answer('Введи время в формате HH:MM, после которого я буду присылать расписание на '
                                     'следующий день',
                                     keyboard=cancel_keyboard())

            elif 'Сменить группу' in message.text:
                if not user.headman:
                    user.action = 'settings_get_new_main_group'
                    await message.answer('Введи новую группу',
                                         keyboard=cancel_keyboard())
                else:
                    await message.answer('Староста не может сменить группу самостоятельно. Если ты действительно '
                                         'сменил группу, напиши об этом обычным текстом, а потом позови человека')

            elif 'Удалить группу' in message.text:
                user_groups = user.group.split(',')
                if len(user_groups) > 2:
                    user.action = 'settings_delete_group'
                    await message.answer('Выбери группу, которую нужно удалить',
                                         keyboard=group_keyboard(groups=user.group.split(',')[1:],
                                                                 enter_other_group=False))

                elif len(user_groups) == 2:
                    user.group = user_groups[0]
                    await message.answer(f'Группа {user_groups[1]} успешно удалена',
                                         keyboard=settings_keyboard(user))

                else:
                    await message.answer('У тебя нет дополнительных групп, поэтому удалять нечего')

            elif 'Добавить группу' in message.text:
                user.action = 'settings_add_group'
                await message.answer('Введи номер группы, которую хочешь добавить')

            elif 'Полное расписание' in message.text:
                user.full_schedule = False if user.full_schedule else True
                await message.answer('Обновил форму расписания',
                                     keyboard=settings_keyboard(user))

            elif 'Уведомления' in message.text:
                pass

            elif 'Присылать расписание' in message.text:
                user.action = 'settings_get_time_for_schedule_sender'
                await message.answer('Введи время, в которое я буду автоматически присылать тебе расписание на '
                                     'следующий день',
                                     keyboard=cancel_keyboard())

            elif 'Помощь' in message.text:
                await message.answer('Раздел находится в разработке')

            elif 'Вернуться назад' in message.text:
                user.action = 'start_menu'
                await message.answer('Возвращаемся в главное меню',
                                     keyboard=standard_keyboard(user))

            else:
                user.action = 'settings_main'
                await message.answer('Возвращаемся в меню настроек',
                                     keyboard=settings_keyboard(user))

        case 'get_schedule_time':
            if 'Отмена' in message.text:
                user.action = 'settings_main'
                await message.answer('Возвращаемся в меню настроек',
                                     keyboard=settings_keyboard(user))

        case 'get_new_group':
            if 'Отмена' in message.text:
                user.action = 'settings_main'
                await message.answer('Возвращаемся в меню настроек',
                                     keyboard=settings_keyboard(user))

        case 'get_time_for_schedule_sender':
            if 'Отмена' in message.text:
                user.action = 'settings_main'
                await message.answer('Возвращаемся в меню настроек',
                                     keyboard=settings_keyboard(user))

        case 'delete_group':
            if 'Отмена' in message.text:
                user.action = 'settings_main'
                await message.answer('Возвращаюсь в меню настроек')

            elif message.text in user.group:
                user_groups = user.group.split(',')
                user_groups.remove(message.text)
                user.group = ','.join(user_groups)
                user.action = 'settings_main'
                await message.answer(f'Группа {message.text} успешно удалена')
                await start_settings(user, message)

            else:
                await message.answer(f'Среди твоих групп нет указанной группы. Пожалуйста, используй клавиатуру')

        case 'add_group':
            if 'Отмена' in message.text:
                user.action = 'settings_main'
                await message.answer('Возвращаюсь в меню настроек')

            elif message.text.lower() in user.group:
                user.action = 'settings_main'
                await message.answer(f'Группа {message.text.lower()} уже есть в списке твоих групп',
                                     keyboard=settings_keyboard(user))

            elif message.text.lower() in groups:
                user.group += f',{message.text.lower()}'
                user.action = 'settings_main'
                await message.answer(f'Группа {message.text.lower()} успешно добавлена')
                await start_settings(user, message)

            else:
                await message.answer('Не могу найти такую группу. Выбери на клавиатуре или попробуй ввести заново',
                                     keyboard=group_keyboard(difflib.get_close_matches(message.text.lower(),
                                                                                       groups,
                                                                                       n=5)))
