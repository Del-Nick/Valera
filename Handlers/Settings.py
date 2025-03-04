import difflib
import re
from datetime import time
from dataclasses import dataclass

from vkbottle.bot import Message

from Server.Core import DB
from Server.Models import User
from Handlers.Keyboards import *
from Scripts.Arrays import GROUPS
from Config.Config import api


@dataclass
class Actions:
    settings: str = 'settings'
    main: str = 'main'
    get_schedule_time: str = 'get_schedule_time'
    get_new_group: str = 'get_new_group'
    get_new_main_group: str = 'get_new_main_group'
    get_new_main_group_alert_sent: str = 'get_new_main_group_alert_sent'
    get_time_for_schedule_sender: str = 'get_time_for_schedule_sender'
    delete_group: str = 'delete_group'
    add_group: str = 'add_group'

    @staticmethod
    def joiner(method: str) -> str:
        return f'settings_{method}'


acts = Actions()


async def start_settings(user: User, message: Message):
    await message.answer(f'VK ID: {user.VkID}')
    answer = (f'Группа:  {user.groups[0]}\n'
              f'{"Доп.группы: " + ', '.join(user.groups[1:]) + "\n" if len(user.groups) > 1 else ''}'
              f'Расписание на следующий день после {user.settings.tomorrow_schedule_after.strftime("%H:%M")}')
    await message.answer(answer,
                         keyboard=settings_keyboard(user))


async def settings(user: User, message: Message) -> User:
    match user.action.replace('settings_', ''):

        case acts.main:
            if 'Время' in message.text:
                user.action = acts.joiner(acts.get_schedule_time)
                await message.answer('Введи время в формате ЧЧ:ММ, после которого я буду присылать расписание на '
                                     'следующий день',
                                     keyboard=cancel_keyboard())

            elif 'Сменить группу' in message.text:
                if not user.settings.headman or user.settings.admin:
                    user.action = acts.joiner(acts.get_new_main_group)
                    await message.answer('Введи новую группу',
                                         keyboard=cancel_keyboard())
                else:
                    await message.answer('Староста не может сменить группу самостоятельно. Если ты действительно '
                                         'сменил группу, напиши об этом обычным текстом, а потом позови человека',
                                         keyboard=settings_keyboard(user))

            elif 'Удалить группу' in message.text:
                await SettingsFunctions.delete_group(user, message)

            elif 'Добавить группу' in message.text:
                user.action = acts.joiner(acts.add_group)
                await message.answer('Введи номер группы, которую хочешь добавить',
                                     keyboard=cancel_keyboard())

            elif 'Всё расписание' in message.text:
                user.settings.full_schedule = not user.settings.full_schedule
                await message.answer('Обновил форму расписания',
                                     keyboard=settings_keyboard(user))

            elif 'Уведомления' in message.text:
                user.settings.notifications = not user.settings.notifications
                await message.answer('Ух, зажжём теперь',
                                     keyboard=settings_keyboard(user))

            elif 'Присылать расписание' in message.text:
                user.action = acts.joiner(acts.get_time_for_schedule_sender)
                await message.answer('Введи время, в которое я буду автоматически присылать тебе расписание на '
                                     'следующий день',
                                     keyboard=cancel_keyboard())

            # TODO: не работает
            elif 'Помощь' in message.text:
                await message.answer('Раздел находится в разработке',
                                     keyboard=settings_keyboard(user))

            elif 'Вернуться назад' in message.text:
                user.action = 'start_menu'
                await message.answer('Возвращаемся в главное меню',
                                     keyboard=standard_keyboard(user))

            else:
                user.action = acts.joiner(acts.main)
                await message.answer('Возвращаемся в меню настроек',
                                     keyboard=settings_keyboard(user))

        case acts.get_schedule_time:
            await SettingsFunctions.change_tomorrow_schedule_after(user, message)

        case acts.get_new_group:
            if 'Отмена' in message.text:
                user.action = acts.joiner(acts.main)
                await message.answer('Возвращаемся в меню настроек',
                                     keyboard=settings_keyboard(user))

        case acts.get_new_main_group | acts.get_new_main_group_alert_sent:
            await SettingsFunctions.change_group(user, message)

        case acts.get_time_for_schedule_sender:
            if 'Отмена' in message.text:
                user.action = acts.joiner(acts.main)
                await message.answer('Возвращаемся в меню настроек',
                                     keyboard=settings_keyboard(user))

        case acts.delete_group:
            await SettingsFunctions.delete_group(user, message)

        case acts.add_group:
            await SettingsFunctions.add_group(user, message)


class SettingsFunctions:
    @staticmethod
    async def change_tomorrow_schedule_after(user: User, message: Message):
        if 'Отмена' in message.text:
            user.action = acts.joiner(acts.main)
            await start_settings(user, message)
        else:
            recognized_time = re.search(r'\d{1,2}:\d{1,2}', message.text)

            if recognized_time:
                hour, minute = map(int, recognized_time.group().split(':'))
                # Если вдруг час будет больше 23, а минуты — 59
                hour, minute = hour % 24, minute % 60
                user.settings.tomorrow_schedule_after = time(hour=hour, minute=minute)
                user.action = acts.joiner(acts.main)
                await message.answer(message=f'Теперь расписание на следующий день я буду присылать тебе после '
                                             f'{user.settings.tomorrow_schedule_after.strftime("%H:%M")}')
                await start_settings(user, message)
            else:
                await message.answer(message=f'Мне не удалось распознать время. Помни, что для меня важен формат ЧЧ:ММ',
                                     keyboard=cancel_keyboard())

    @staticmethod
    async def delete_group(user: User, message: Message):
        match user.action.replace('settings_', ''):
            case 'main':
                # Вызывается из меню настроек
                if len(user.groups) > 2:
                    user.action = acts.joiner(acts.delete_group)
                    await message.answer('Выбери группу, которую нужно удалить',
                                         keyboard=group_keyboard(groups=user.groups[1:],
                                                                 enter_other_group=False))

                elif len(user.groups) == 2:
                    deleted_group = user.groups.pop(-1)
                    await message.answer(f'Группа {deleted_group} успешно удалена',
                                         keyboard=settings_keyboard(user))
                    await start_settings(user, message)

                else:
                    await message.answer('У тебя нет дополнительных групп, поэтому удалять нечего')
                    await start_settings(user, message)

            case 'delete_group':
                # Вызывается после возможности выбрать группу для удаления
                if 'Отмена' in message.text:
                    user.action = acts.joiner(acts.main)
                    await message.answer('Возвращаюсь в меню настроек')
                    await start_settings(user, message)

                elif message.text in user.groups:
                    user.groups.remove(message.text)
                    user.action = acts.joiner(acts.main)
                    await message.answer(f'Группа {message.text} успешно удалена')
                    await start_settings(user, message)

                else:
                    await message.answer(f'Среди твоих групп нет указанной группы. Пожалуйста, используй клавиатуру')

    @staticmethod
    async def change_group(user: User, message: Message):
        if 'Отмена' in message.text:
            user.action = acts.joiner(acts.main)
            await message.answer('Возвращаюсь в меню настроек')
            await start_settings(user, message)

        elif message.text.lower() in GROUPS:
            if message.text.lower() in user.groups[1:]:
                user.groups.remove(message.text.lower())
            user.groups[0] = message.text.lower()
            await message.answer(f'Твоя основная группа изменена на {user.groups[0]}')
            await start_settings(user, message)

            if user.action == acts.get_new_main_group_alert_sent:
                await api.messages.send(peer_id=2000000001, random_id=0,
                                        message=f'Пользователь {user.VkFirstName} {user.VkLastName} всё-таки смог '
                                                f'ввести группу самостоятельно. Всем спасибо. Расходимся')

            user.action = acts.joiner(acts.main)

        elif message.text == 'Нет нужной группы':
            await message.answer('Я сообщил админам, что у тебя возникли проблемы. Как только появится '
                                 'возможность, тебе сразу же ответят')
            await api.messages.send(peer_id=2000000001, random_id=0,
                                    message=f'Пользователь {user.VkFirstName} {user.VkLastName} '
                                            f'не может правильно ввести группу. Срочно требуется помощь. '
                                            f'Уиуиуиуиуи 🚨🚨🚨\n\n'
                                            f'Ссылка на переписку: https://vk.com/gim34300772?sel={user.VkID}')

        else:
            await message.answer(
                f'Не могу найти группу. Постарался найти похожие варианты и добавить на клавиатуре',
                keyboard=group_keyboard(difflib.get_close_matches(message.text.lower(), GROUPS, n=5)))

    @staticmethod
    async def add_group(user: User, message: Message):
        if 'Отмена' in message.text:
            user.action = acts.joiner(acts.main)
            await message.answer('Возвращаюсь в меню настроек')

        elif message.text.lower() in user.groups:
            user.action = acts.joiner(acts.main)
            await message.answer(f'Группа {message.text.lower()} уже есть в списке твоих групп')
            await start_settings(user, message)

        elif message.text.lower() in GROUPS:
            user.groups.append(message.text.lower())
            user.action = acts.joiner(acts.main)
            await message.answer(f'Группа {message.text.lower()} успешно добавлена')
            await start_settings(user, message)

        elif message.text == 'Нет нужной группы':
            await message.answer('Я сообщил админам, что у тебя возникли проблемы. Как только появится '
                                 'возможность, тебе сразу же ответят')

            await api.messages.send(peer_id=2000000001, random_id=0,
                                    message=f'Пользователь {user.VkFirstName} {user.VkLastName} '
                                            f'не может правильно ввести группу. Срочно требуется помощь. '
                                            f'Уиуиуиуиуи 🚨🚨🚨\n\n'
                                            f'Ссылка на переписку: https://vk.com/gim34300772?sel={user.VkID}')

        else:
            await message.answer(
                f'Не могу найти группу. Постарался найти похожие варианты и добавить на клавиатуре',
                keyboard=group_keyboard(difflib.get_close_matches(message.text.lower(), GROUPS, n=5)))
