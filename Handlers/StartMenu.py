import difflib

from Server.DB import User
from Files.Files import *
from Handlers.Keyboards import *
from Handlers.Settings import start_settings
from Scripts.Arrays import groups

from vkbottle.bot import Message
from datetime import datetime, timedelta
import re


async def start_menu(user: User, message: Message):
    if 'menu' in user.action:
        if 'ДЗ' in message.text:
            user.action = 'start_homework'

        elif 'Учебники' in message.text:
            await message.answer('Пока не готов раздел')

        elif 'Праки' in message.text:
            await message.answer('Пока не готов раздел')

        elif 'Расписание' in message.text:
            if 'start_menu_after_schedule' in user.action:
                if 'Ввести другую группу' in message.text:
                    user.action = 'start_menu_after_schedule_get_temp_group'
                    await message.answer('Введи новую группу')

                elif user.action == 'start_menu_after_schedule_get_temp_group':
                    if message.text.lower() in groups:
                        user.action = f'start_menu_after_schedule_group_{message.text.lower()}'
                        await schedule_builder(user, message, True)
                    else:
                        await message.answer('Не могу найти такую группу. Воспользуйся клавиатурой или попробуй ввести '
                                             'заново',
                                             keyboard=group_keyboard(difflib.get_close_matches(message.text.lower(),
                                                                                               groups,
                                                                                               n=5)))
                else:
                    await schedule_builder(user, message, additional_info=True)
            else:
                if 'group' not in user.action:
                    user.action = f'start_menu_after_schedule_group_{user.group.split(",")[0]}'
                await schedule_builder(user, message)

        elif 'На неделю' in message.text:
            user.action = 'start_menu_after_week_schedule'
            await week_schedule_builder(user, message)

        elif 'Настройки' in message.text:
            user.action = 'settings_main'
            await start_settings(user, message)

        else:
            await message.answer(message.text,
                                 keyboard=standard_keyboard(user))
    else:
        user.action = 'start_menu'


async def back_to_start(user: User, message: Message):
    if message.text == 'Валера стереть':
        if await user.delete_row():
            await message.answer('Запись о тебе удалена')
        else:
            await message.answer('У тебя недостаточно прав для доступа')

    else:
        user.action = 'start_menu'
        await user.update()
        await message.answer('Любовь, надежда и вера-а-а', keyboard=standard_keyboard(user))


async def schedule_builder(user: User, message: Message, additional_info: bool = False):
    def get_additional_info(day: int, group: str):

        if message.text in ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']:
            day = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ'].index(message.text)

        elif message.text in groups:
            group = message.text
            user.action = f'start_menu_after_schedule_group_{group}'

        return day, group

    group = user.action.split('_')[-1]

    if group in schedule.keys():
        data = schedule[group]
        week_number = datetime.today().isocalendar().week - 5
        day = datetime.today().weekday()
        date = datetime.now()

        if day == 6:
            day = 0
            date += timedelta(days=1)
            week_number += 1
        elif datetime.now().strftime('%H:%M') > user.schedule_next_day_after:
            if day == 5:
                day = 0
                date += timedelta(days=2)
                week_number += 1
            else:
                day += 1
                date += timedelta(days=1)

        if additional_info:
            day, group = get_additional_info(day, group)
            data = schedule[group]

        answer = list(data.keys())[day].upper() + ', ' + date.strftime('%d.%m') + '\n\n'

        name_day = list(data.keys())[day]

        # чётность недели
        parity = 'even' if week_number % 2 == 1 else 'odd'

        num_of_lessons = 0

        if user.full_schedule:
            for lesson in data[name_day].keys():
                _ = data[name_day][lesson][parity]
                if _["lesson"] != '':
                    time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40',
                            '18:55-20:30']
                    answer += f'{time[int(lesson) - 1]}  {_["lesson"]}  {_["room"]}\n{_["teacher"]}\n\n'
                    num_of_lessons += 1
        else:
            for lesson in data[name_day].keys():
                temp = data[name_day][lesson][parity]
                if temp["lesson"] != '':
                    time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40',
                            '18:55-20:30']
                    answer += f'{time[int(lesson) - 1]}  {temp["lesson"]}  {temp["room"]}\n'
                    num_of_lessons += 1

        if num_of_lessons == 1:
            answer += '\nУ тебя 1 пара'
        elif num_of_lessons < 5:
            answer += f'\nУ тебя {num_of_lessons} пары'
        else:
            answer += f'\nУ тебя {num_of_lessons} пар'

        await message.answer(answer, keyboard=after_schedule_keyboard(user, day))

    else:
        return 'Неловко-то как!.. Кажется, я не смог найти твоё расписание. Уже сообщил, куда следует.. &#128580;'


async def week_schedule_builder(user: User, message: Message):
    group = user.group.split(',')[0]

    if group in schedule.keys():
        data = schedule[group]
        week_number = datetime.today().isocalendar().week - 5

        day = datetime.today().weekday()
        date = datetime.now()

        next_week = False

        if day == 6:
            day = 0
            date += timedelta(days=1)
            next_week = True
            week_number += 1
        elif datetime.now().strftime('%H:%M') > user.schedule_next_day_after:
            if day == 5:
                day = 0
                date += timedelta(days=2)
                next_week = False
                week_number += 1
            else:
                day += 1
                date += timedelta(days=1)

        answer = list(data.keys())[day].upper() + ', ' + date.strftime('%d.%m') + '\n\n'

        day = list(data.keys())[day]

        # чётность недели
        parity = 'even' if week_number % 2 == 1 else 'odd'

        for day_of_week in data.keys():
            if next_week:
                answer += day_of_week.upper() + ', ' + (
                        date - timedelta(days=date.weekday() - list(data.keys()).index(day_of_week) - 7)).strftime(
                    '%d.%m') + '\n\n'
            else:
                answer += day_of_week.upper() + ', ' + (
                        date - timedelta(days=date.weekday() - list(data.keys()).index(day_of_week))).strftime(
                    '%d.%m') + '\n\n'
            for lesson in data[day_of_week].keys():
                temp = data[day][lesson][parity]
                if temp["lesson"] != '':
                    time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40',
                            '18:55-20:30']
                    answer += f'{time[int(lesson) - 1]}  {temp["lesson"]}  {temp["room"]}\n'

        num_of_lessons = len(answer.split('\n')) - 3

        if num_of_lessons == 1:
            answer += '\nУ тебя 1 пара'
        elif num_of_lessons < 5:
            answer += f'\nУ тебя {num_of_lessons} пары'
        else:
            answer += f'\nУ тебя {num_of_lessons} пар'

        await message.answer(answer, keyboard=after_schedule_keyboard(user))

    else:
        return 'Неловко-то как!.. Кажется, я не смог найти твоё расписание. Уже сообщил, куда следует.. &#128580;'
