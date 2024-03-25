from Server.DB import User
from Files.Files import *
from Handlers.Keyboards import *

from vkbottle.bot import Message
from datetime import datetime, timedelta
import re


async def start_menu(user: User, message: Message):
    match user.action.replace('start_', ''):

        case 'menu':
            # удалили всё, кроме букв русского алфавита
            match re.sub(r'[^А-Яа-я]', '', message.text):

                case 'ДЗ':
                    user.action = 'start_homework'

                case 'Учебники':
                    await message.answer('Пока не готов раздел')

                case 'Праки':
                    await message.answer('Пока не готов раздел')

                case 'Расписание':
                    await schedule_builder(user, message)

                case 'На неделю':
                    await week_schedule_builder(user, message)

                case 'Настройки':
                    user.action = 'settings_main'
                    await start_settings(user, message)

                case _:
                    await message.answer(message.text,
                                         keyboard=standard_keyboard(user))

    await user.update()


async def back_to_start(user: User, message: Message):
    if message.text == 'Валера стереть':
        await user.delete_row()

    else:
        user.action = 'start_menu'
        await user.update()
        await message.answer('Любовь, надежда и вера-а-а', keyboard=standard_keyboard(user))


async def start_settings(user: User, message: Message):
    await message.answer(f'VK ID: {user.vk_id}')
    await message.answer(f'Группа:  {user.group.split(",")[0]}')

    if len(user.group.split(",")) > 1:
        groups = ', '.join(user.group.split(",")[1:])
    else:
        groups = 'Нет'

    await message.answer(f'Доп. группы:  {groups}')
    await message.answer(f'Расписание на следующий день после {user.schedule_next_day_after}',
                         keyboard=settings_keyboard(user))


async def schedule_builder(user: User, message: Message):
    group = user.group.split(',')[0]

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

        answer = list(data.keys())[day].upper() + ', ' + date.strftime('%d.%m') + '\n\n'

        day = list(data.keys())[day]

        # чётность недели
        parity = 'even' if week_number % 2 == 1 else 'odd'

        for lesson in data[day].keys():
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
