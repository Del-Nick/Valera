import difflib
import os

from Server.DB import User
from Files.Files import *
from Handlers.Keyboards import UserKeyboards
from Handlers.Settings import start_settings
from Scripts.Arrays import groups
from Scripts.Rooms import check_rooms, rooms
from Config.Config import uploader

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
            if 'group' not in user.action:
                user.action = f'start_menu_after_schedule_group_{user.group.split(",")[0]}'
            await schedule_builder(user, message)

        elif 'На неделю' in message.text:
            if 'group' not in user.action:
                user.action = f'start_menu_after_week_schedule_group_{user.group.split(",")[0]}'
            await week_schedule_builder(user, message)

        elif 'Настройки' in message.text:
            user.action = 'settings_main'
            await start_settings(user, message)

        elif check_rooms(message.text):
            room, floor, part = check_rooms(message.text)
            await message.answer(part)
            path = rooms(room, floor)
            scheme = await uploader.upload(file_source=f'{path}')
            await message.answer('Нужный кабинет обозначен оранжевым цветом &#128521;', attachment=scheme)
            os.remove(path)

        elif 'start_menu_after_schedule' in user.action:
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
                                         keyboard=UserKeyboards.group_keyboard(
                                             groups=difflib.get_close_matches(message.text.lower(),
                                                                              groups,
                                                                              n=5)))
            else:
                await schedule_builder(user, message, additional_info=True)

        elif 'start_menu_after_week_schedule' in user.action:
            if 'Ввести другую группу' in message.text:
                user.action = 'start_menu_after_week_schedule_get_temp_group'
                await message.answer('Введи новую группу')

            elif user.action == 'start_menu_after_week_schedule_get_temp_group':
                if message.text.lower() in groups:
                    user.action = f'start_menu_after_week_schedule_group_{message.text.lower()}'
                    await week_schedule_builder(user, message, additional_info=True)
                else:
                    await message.answer('Не могу найти такую группу. Воспользуйся клавиатурой или попробуй ввести '
                                         'заново',
                                         keyboard=UserKeyboards.group_keyboard(
                                             groups=difflib.get_close_matches(message.text.lower(),
                                                                              groups,
                                                                              n=5)))
            else:
                await week_schedule_builder(user, message, additional_info=True)

        else:
            await message.answer(message.text,
                                 keyboard=UserKeyboards.standard_keyboard(user))

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
        await message.answer('Любовь, надежда и вера-а-а', keyboard=UserKeyboards.standard_keyboard(user))


async def schedule_builder(user: User, message: Message, additional_info: bool = False):
    group = user.action.split('_')[-1].replace('group_', '')

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

        # Эта штука нужна, чтобы обработать нажатия inline клавиатуры после сообщения с расписанием
        if additional_info:
            if message.text in ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']:
                day = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ'].index(message.text)

            elif message.text in groups:
                group = message.text
                user.action = replace_parameters_in_action(user.action, group=group)
            data = schedule[group]

        answer = list(data.keys())[day].upper() + ', ' + date.strftime('%d.%m') + '\n\n'

        name_day = list(data.keys())[day]

        print(user.action)

        # чётность недели
        parity = 'even' if week_number % 2 == 1 else 'odd'

        num_of_lessons = 0

        if user.full_schedule:
            for lesson in data[name_day].keys():
                _ = data[name_day][lesson][parity]
                if _["lesson"] != '':
                    time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40',
                            '18:55-20:30']
                    answer += f'{time[int(lesson) - 1]} {_["lesson"]}\n'

                    if _["room"] != '':
                        answer += f'  📍  {_["room"]}\n'

                    if _["teacher"] != '':
                        answer += f'  👨‍🏫  {_["teacher"]}\n\n'

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

        await message.answer(answer, keyboard=UserKeyboards.after_schedule_keyboard(user, day))

    else:
        return 'Неловко-то как!.. Кажется, я не смог найти твоё расписание. Уже сообщил, куда следует.. &#128580;'


async def week_schedule_builder(user: User, message: Message, additional_info: bool = False):
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

        # Эта штука нужна, чтобы обработать нажатия inline клавиатуры после сообщения с расписанием
        if additional_info:
            if message.text in groups:
                group = message.text
                user.action = replace_parameters_in_action(user.action, group=group)
                data = schedule[group]

            elif 'Нечётная' in message.text and week_number % 2 == 0:
                week_number += 1

            elif 'Чётная' in message.text and week_number % 2 == 1:
                week_number += 1

        answer = list(data.keys())[day].upper() + ', ' + date.strftime('%d.%m') + '\n\n'

        parity = 'even' if week_number % 2 == 1 else 'odd'

        if user.full_schedule:
            await message.answer(f'НЕДЕЛЯ №{week_number}')
            for num, day_of_week in enumerate(data.keys()):
                if next_week:
                    answer = day_of_week.upper() + ', ' + (
                            date - timedelta(days=date.weekday() - list(data.keys()).index(day_of_week) - 7)).strftime(
                        '%d.%m') + '\n\n'
                else:
                    answer = day_of_week.upper() + ', ' + (
                            date - timedelta(days=date.weekday() - list(data.keys()).index(day_of_week))).strftime(
                        '%d.%m') + '\n\n'

                for lesson in data[day_of_week].keys():
                    _ = data[day_of_week][lesson][parity]
                    if _["lesson"] != '':
                        time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40',
                                '18:55-20:30']
                        answer += f'{time[int(lesson) - 1]}  {_["lesson"]}\n'

                        if _["room"] != '':
                            answer += f'  📍  {_["room"]}\n'

                        if _["teacher"] != '':
                            answer += f'  👨‍🏫  {_["teacher"]}\n\n'

                if num == len(data.keys()) - 1:
                    await message.answer(answer,
                                         keyboard=UserKeyboards.after_schedule_keyboard(user=user,
                                                                                        week_schedule=True,
                                                                                        parity=parity))
                else:
                    await message.answer(answer)
        else:
            answer = f'НЕДЕЛЯ №{week_number}\n\n'
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
                    temp = data[day_of_week][lesson][parity]
                    if temp["lesson"] != '':
                        time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40',
                                '18:55-20:30']
                        answer += f'{time[int(lesson) - 1]}  {temp["lesson"]}  {temp["room"]}\n'

                answer += '\n\n'

            await message.answer(answer, keyboard=UserKeyboards.after_schedule_keyboard(user,
                                                                                        week_schedule=True,
                                                                                        parity=parity))

    else:
        return 'Неловко-то как!.. Кажется, я не смог найти твоё расписание. Уже сообщил, куда следует.. &#128580;'


def replace_parameters_in_action(action, group: str = None):
    action = action.split('_')

    if group is not None:
        action[-1] = f'group_{group}'

    return '_'.join(action)
