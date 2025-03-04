import difflib
from pprint import pprint

from natsort import natsorted
from vkbottle import Bot
from vkbottle.http import aiohttp

from Config.Config import doc_uploader, api, GETTING_ERROR
from Files.Files import *
from Handlers.Keyboards import *
from Handlers.Settings import start_settings
from Scripts.Arrays import GROUPS, workshop_rooms
from Server.Core import DB, BooksDB, HomeworksDB, WorkshopsDB, SessionDB, LessonScheduleDB, CustomLessonScheduleDB
from Scripts.FloorCabinetSearchEngine import check_rooms, rooms
from Handlers.Event import event_schedule, Keyboards

from vkbottle.bot import Message
from datetime import datetime, timedelta
import re

from Server.Models import Books, Workshops, WeekType


weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']


async def start_menu(user: User, message: Message):
    if 'ДЗ' in message.text or 'homeworks' in user.action:
        await get_and_send_homeworks(user, message)

    elif 'Учебники' in message.text or 'books' in user.action:
        await get_and_send_books(user, message)

    elif 'Праки' in message.text or 'workshops' in user.action:
        await get_and_send_workshops(user, message)

    elif 'Расписание' in message.text:
        await schedule_builder(user, message)
        user.action = 'start_menu_after_schedule'

    elif 'Сессия' in message.text:
        await message.answer('Поздравляем тебя с окончанием сессии! Наконец-то чиииллл...',
                             keyboard=standard_keyboard(user))

    elif user.action == 'start_menu_session':
        await process_session_schedule(user, message)

    # elif 'день российской науки' in message.text.lower():
    #     user.action = 'event'
    #     await message.answer(message=event_schedule,
    #                          keyboard=Keyboards.main_keyboard())

    elif 'Настройки' in message.text:
        user.action = 'settings_main'
        await start_settings(user, message)

    elif 'Панель админа' in message.text and user.settings.admin:
        await message.answer('Панель админа реализована в телеграме, пожалуйста, пользуйся ей. Здесь пока доступна '
                             'только дозагрузка учебников, которые не удалось загрузить через телеграм.\n\n'
                             ''
                             'Пришли мне один учебник с точно таким же названием, как и в телеграме. Вводи описание '
                             'по образцу: "курс -семестр -предмет"',
                             keyboard=cancel_keyboard())
        user.action = 'admin_get_book'

    elif 'Cтароста' in message.text:
        await message.answer('Режим старосты пока не поддерживается ВК. Пожалуйста, используй его в Телеграме '
                             '(https://t.me/studsovet_ff_bot)')

    elif check_rooms(message) and user.action == 'start_menu':
        await rooms(user, message)

    elif user.action.startswith('start_menu_after_schedule'):
        if 'Сообщить об ошибке' in message.text:
            user.action = 'start_menu_get_error_description'
            await message.answer('Опиши, где именно ошибка: группа, день недели, какая-то дополнительная информация')

        elif 'Ввести другую группу' in message.text:
            user.action = 'start_menu_after_schedule_get_temp_group'
            await message.answer('Введи новую группу')

        elif message.text == 'Назад':
            user.action = 'start_menu'
            await message.answer('Возвращаюсь в главное меню',
                                 keyboard=standard_keyboard(user))

        elif user.action == 'start_menu_after_schedule_get_temp_group':
            if message.text.lower() in GROUPS:
                user.action = f'start_menu_after_schedule_group={message.text.lower()}'
                await schedule_builder(user, message)

            elif message.text == 'Отмена':
                user.action = 'start_menu'
                await message.answer('Возвращаюсь в главное меню',
                                     keyboard=standard_keyboard(user))

            else:
                await message.answer('Не могу найти такую группу. Воспользуйся клавиатурой или попробуй ввести '
                                     'заново',
                                     keyboard=group_keyboard(difflib.get_close_matches(message.text.lower(),
                                                                                       GROUPS,
                                                                                       n=5)))

        elif message.text in ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ'] or message.text.lower() in GROUPS:
            await schedule_builder(user, message)

        else:
            user.action = 'start_menu'
            await message.answer('Не совсем тебя понял. Возвращаюсь в главное меню',
                                 keyboard=standard_keyboard(user))

    elif check_rooms(message):
        await rooms(user, message)

    elif user.action == 'start_menu_get_error_description':
        user.action = 'start_menu'
        await message.answer('Твоё сообщение передано админам группы. Спасибо за бдительность!',
                             keyboard=standard_keyboard(user))
        if GETTING_ERROR:
            await api.messages.send(peer_id=2000000001, random_id=0,
                                    message=f'Пользователь {user.VkFirstName} {user.VkLastName} '
                                            f'поймал ошибку в расписании Уиуиуиуиуи 🚨🚨🚨\n\n'
                                            f'Ссылка на переписку: https://vk.com/gim34300772?sel={user.VkID}\n\n'
                                            f'Описание ошибки от {user.VkFirstName}:\n\n{message.text}')

    else:
        user.action = 'start_menu'
        await message.answer('Не совсем тебя понял',
                             keyboard=standard_keyboard(user))


async def get_and_send_homeworks(user: User, message: Message):
    homeworks = await HomeworksDB.select_homeworks(user.groups[0])

    if homeworks.homeworks:
        if 'ДЗ' in message.text:
            user.action = 'start_homeworks'
            buttons = [x for x in homeworks.homeworks.keys()]
            await message.answer('Выбери предмет, по которому хочешь получить домашние задания',
                                 keyboard=custom_keyboard(buttons=buttons))

        elif 'Назад' in message.text:
            user.action = 'start_menu'
            await message.answer('Возвращаюсь в главное меню',
                                 keyboard=standard_keyboard(user))

        elif message.text in homeworks.homeworks.keys():
            subject = message.text

            if homeworks.homeworks[subject]:
                for i, homework in enumerate(homeworks.homeworks[subject]):
                    media = [attach['vk_file_id'] for attach in homework['attachments']]

                    if homework['text']:
                        await message.answer(f'{i + 1}. {homework['text']}\n\n'
                                             f'Дата добавления: {homework['date']}',
                                             attachment=media)

                    else:
                        await message.answer(f'{i + 1}. {homework['text']}\n\n'
                                             f'Дата добавления: {homework['date']}',
                                             attachment=media)

                buttons = [x for x in homeworks.homeworks.keys()]
                await message.answer('Выбери предмет, по которому хочешь получить домашние задания',
                                     keyboard=custom_keyboard(buttons=buttons))

            else:
                buttons = [x for x in homeworks.homeworks.keys()]
                await message.answer('Домашние задания по этому предмету не добавлены. Выбери другой предмет, '
                                     'по которому хочешь получить домашние задания',
                                     keyboard=custom_keyboard(buttons=buttons))

        else:
            buttons = [x for x in homeworks.homeworks.keys()]
            await message.answer('Не смог найти такой предмет. Пожалуйста, пользуйся клавиатурой',
                                 keyboard=custom_keyboard(buttons=buttons))

    else:
        user.action = 'start_menu'
        await message.answer('Кажется, твой староста ещё не добавлял домашние задания. Если ты староста или хочешь '
                             'руководить вложениями в группе, напиши @id318861079 (Кате)',
                             keyboard=standard_keyboard(user))


async def get_and_send_workshops(user: User, message: Message):
    workshops: Workshops = await WorkshopsDB.select_workshops(user.groups[0][0])
    semester = '2 семестр' if 1 < datetime.now().month < 7 else '1 семестр'

    if workshops.workshops:
        if 'Праки' in message.text:
            if len(list(workshops.workshops.keys())) == 1:
                subject = list(workshops.workshops[semester].keys())[0]
                user.action = f'start_workshops_subject={subject}_get_num'

                buttons = natsorted([x['num'] for x in workshops.workshops[semester][subject]])
                await message.answer('Выбери номер практикума',
                                     keyboard=custom_keyboard(buttons=buttons, buttons_in_row=5))

            else:
                user.action = f'start_workshops_get_subject'
                subjects = list(workshops.workshops[semester].keys())
                buttons = natsorted([x for x in subjects])
                await message.answer('Выбери предмет',
                                     keyboard=custom_keyboard(buttons=buttons, buttons_in_row=5))

        elif 'get_num' in user.action:
            subject = re.search(r'subject=[0-9a-zA-Zа-яА-Я .]{1,20}', user.action).group().replace('subject=', '')

            if message.text in [x['num'] for x in workshops.workshops[semester][subject]]:
                num = message.text

                for i, book in enumerate(workshops.workshops[semester][subject]):
                    try:
                        room = f'\n\n📍 {workshop_rooms[subject][book['num']]}'
                    except KeyError:
                        room = ''

                    if book['num'] == num:
                        await message.answer(book['name'] + room,
                                             attachment=book['vk_file_id'])

                buttons = natsorted([x['num'] for x in workshops.workshops[semester][subject]])
                await message.answer('Выбери номер практикума',
                                     keyboard=custom_keyboard(buttons=buttons, buttons_in_row=5))

            elif 'Назад' in message.text:
                if len(list(workshops.workshops.keys())) == 1:
                    subject = list(workshops.workshops.keys())[0]
                    semester = semester if subject in workshops.workshops[semester].keys() else '2 семестр'
                    user.action = f'start_workshops_subject={subject}_get_num'

                    buttons = natsorted([x['num'] for x in workshops.workshops[semester][subject]])
                    await message.answer('Выбери номер практикума',
                                         keyboard=custom_keyboard(buttons=buttons, buttons_in_row=5))

                else:
                    user.action = f'start_workshops_get_subject'
                    subjects = list(workshops.workshops[semester].keys())
                    buttons = natsorted([x for x in subjects])
                    await message.answer('Выбери предмет',
                                         keyboard=custom_keyboard(buttons=buttons, buttons_in_row=5))

            else:
                buttons = natsorted([x['num'] for x in workshops.workshops[semester][subject]])
                await message.answer('Кажестя, я не знаю такую методичку. Пожалуйста, пользуйся клавиатурой',
                                     keyboard=custom_keyboard(buttons=buttons, buttons_in_row=5))

        elif 'get_subject' in user.action:
            if 'Назад' in message.text:
                user.action = 'start_menu'
                await message.answer('Возвращаюсь в главное меню',
                                     keyboard=standard_keyboard(user))

            else:
                subject = message.text
                user.action = f'start_workshops_subject={subject}_get_num'

                buttons = natsorted([x['num'] for x in workshops.workshops[semester][subject]])
                await message.answer('Выбери номер практикума',
                                     keyboard=custom_keyboard(buttons=buttons, buttons_in_row=5))

    else:
        await message.answer('Странно.. Не смог найти методички практикумов',
                             keyboard=standard_keyboard(user))


async def get_and_send_books(user: User, message: Message):
    books: Books = await BooksDB.select_books(user.groups[0][0])
    semester = '2 семестр' if 1 < datetime.now().month < 7 else '1 семестр'

    if books.books:
        if 'subject' not in user.action:
            buttons = list(books.books[semester].keys())
            await message.answer('Выбери предмет', keyboard=custom_keyboard(buttons=buttons))
            user.action = 'start_books_subject'

        elif message.text == 'Назад':
            await message.answer('Возвращаюсь в главное меню', keyboard=standard_keyboard(user))
            user.action = 'start_menu'

        else:
            if message.text not in books.books[semester].keys():
                await message.answer('Не удалось распознать предмет', keyboard=standard_keyboard(user))
                user.action = 'start_menu'

            else:
                subject = message.text

                media = []

                for num, book in enumerate(books.books[semester][subject]):
                    if books.books[semester][subject][num]['type'] == 'document':
                        media.append(books.books[semester][subject][num]['vk_file_id'])

                    else:
                        media.append(books.books[semester][subject][num]['vk_file_id'])

                await message.answer(subject,
                                     attachment=media)
                buttons = list(books.books[semester].keys())
                await message.answer('Ты можешь выбрать другой предмет',
                                     keyboard=custom_keyboard(buttons=buttons))

    else:
        await message.answer('Учебники ещё не добавлены',
                             keyboard=standard_keyboard(user))


async def back_to_start(user: User, message: Message):
    if user.groups:
        user.action = 'start_menu'

        await message.answer('Любовь, надежда и вера-а-а', keyboard=standard_keyboard(user))

    elif not user.groups:
        await message.answer('Для работы мне необходимо знать твою группу. Подожди немного, '
                             'скоро мы со всем разберёмся', keyboard=standard_keyboard(user))


async def schedule_builder(user: User, message: Message):
    if message.text in GROUPS:
        group = message.text
        user.action = f'start_menu_after_schedule_group={group}'

    else:
        group = user.action.replace('start_menu_after_schedule_group=', '') if 'group' in user.action else user.groups[
            0]

    time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40',
            '18:55-20:30']

    week_number = datetime.today().isocalendar().week - 5

    if message.text in ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']:
        day = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ'].index(message.text)
        date = datetime.now() - timedelta(days=datetime.now().weekday() - day)
        if datetime.now().weekday() > 4 and datetime.now().time() > user.settings.tomorrow_schedule_after:
            date += timedelta(days=7)
            week_number += 1

    else:
        day = datetime.today().weekday()
        date = datetime.now()

        if day == 6:
            day = 0
            date += timedelta(days=1)
            week_number += 1
        elif datetime.now().time() > user.settings.tomorrow_schedule_after:
            if day == 5:
                day = 0
                date += timedelta(days=2)
                week_number += 1
            else:
                day += 1
                date += timedelta(days=1)

    lessons = await LessonScheduleDB.select(group_name=group, weekday=day,
                                            week_type=WeekType.ODD if week_number % 2 == 1 else WeekType.EVEN)
    custom_lessons = await CustomLessonScheduleDB.select(group_name=group, weekday=day,
                                                         week_type=WeekType.ODD if week_number % 2 == 1 else WeekType.EVEN)

    answer = f'Расписание для группы {group}\n\n' if group != user.groups[0] else ''
    answer += weekdays[day].upper() + ', ' + date.strftime(
        '%d.%m') + f' ______ Неделя № {week_number}' + '\n\n'

    if lessons:
        schedule = {lesson.lesson_number: lesson for lesson in lessons}
        custom_schedule = {lesson.lesson_number: lesson for lesson in custom_lessons}

        lessons = [schedule[x] for x in sorted(list(schedule.keys()))]

        for i, lesson in enumerate(lessons):
            for custom_lesson in custom_lessons:
                if custom_lesson:
                    if (custom_lesson.group_id == lesson.group_id and
                            custom_lesson.weekday == lesson.weekday and
                            custom_lesson.week_type == lesson.week_type and
                            custom_lesson.lesson_number == lesson.lesson_number):
                        lessons[i] = custom_lesson

        answer = f'Расписание для группы {group}\n\n' if group != user.groups[0] else ''
        answer += weekdays[day].upper() + ', ' + date.strftime(
            '%d.%m') + f' ______ Неделя № {week_number}' + '\n\n'

        if lessons[0].lesson_number > 1:
            for _ in range(lessons[0].lesson_number):
                answer += f'{time[_]}\n'

        for lesson in lessons:
            if user.settings.full_schedule:
                answer += f'{time[lesson.lesson_number - 1]}  {lesson.lesson}  {lesson.room}\n{lesson.teacher}\n\n'
            else:
                answer += f'{time[lesson.lesson_number - 1]}  {lesson.lesson}  {lesson.room}\n\n'

        if len(lessons) == 1:
            answer += '\nУ тебя 1 пара'
        elif 0 < len(lessons) < 5:
            answer += f'\nУ тебя {len(lessons)} пары'
        else:
            answer += f'\nУ тебя {len(lessons)} пар'

        await message.answer(answer, keyboard=after_schedule_keyboard(user=user, day=day, group=group))

    else:
        await message.answer(f'{answer}\n\nУ тебя 0 пар',
                             keyboard=after_schedule_keyboard(user=user, group=group, day=day))


async def process_session_schedule(user: User, message: Message):
    if message.text == 'Назад':
        user.action = 'start_menu'
        await message.answer('Возвращаюсь в главное меню',
                             keyboard=standard_keyboard(user))
        return

    if message.text in GROUPS:
        group = message.text
    else:
        group = user.groups[0]

    exams = await SessionDB.select(group)

    if exams:
        remaining_exams = [exam for exam in exams if exam.exam_datetime > datetime.now()]
        count_remaining_exams = len(remaining_exams)

        if count_remaining_exams > 4:
            answer = f'Тебе осталось всего {count_remaining_exams} экзаменов\n\n'
        elif count_remaining_exams > 1:
            answer = f'Тебе осталось всего {count_remaining_exams} экзамена\n\n'
        else:
            answer = 'Тебе остался всего 1 экзамен\n\n'

        for exam in exams:
            if user.settings.full_schedule:
                answer += (f'📅 {exam.exam_datetime.strftime('%d.%m %H:%M')} — {exam.room}\n'
                           f'{exam.name}\n'
                           f'-- {exam.teacher}\n\n\n')
            else:
                answer += (f'📅 {exam.exam_datetime.strftime('%d.%m %H:%M')} — {exam.room}\n'
                           f'{exam.name}\n\n\n')

        answer += f'\n\nДо ближайшего экзамена осталось '
        distance_between_datetimes = remaining_exams[0].exam_datetime - datetime.now()

        hours, remainder = divmod(distance_between_datetimes.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if distance_between_datetimes.days > 0:
            if distance_between_datetimes.days > 4:
                answer += f'{distance_between_datetimes.days} дней '
            elif distance_between_datetimes.days > 1:
                answer += f'{distance_between_datetimes.days} дня '
            else:
                answer += f'{distance_between_datetimes.days} день '

        if hours > 0:
            if hours in [2, 3, 4, 22, 23]:
                answer += f'{hours} часа '
            elif hours in [1, 21]:
                answer += f'{hours} час '
            else:
                answer += f'{hours} часов '

        if minutes > 0:
            if minutes in [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54]:
                answer += f'{minutes} минуты '
            elif minutes in [1, 21, 31, 41, 51]:
                answer += f'{minutes} минута '
            else:
                answer += f'{minutes} минут '

        if seconds > 0:
            if seconds in [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54]:
                answer += f'{minutes} минут '
            elif seconds in [1, 21, 31, 41, 51]:
                answer += f'{seconds} секунда'
            else:
                answer += f'{seconds} секунд'

        answer += ('\n\n___________________________\n'
                   'P.s. В расписании могут быть ошибки. На всякий случай проверь по файлу от учебной части\n'
                   'P.p.s. Формат отображения (вывод преподавателей) можно изменить в настройках')
        buttons = [other_group for other_group in user.groups if other_group != group]
        await message.answer(message=answer,
                             keyboard=custom_keyboard(buttons=buttons,
                                                      buttons_in_row=5))

    else:
        buttons = [other_group for other_group in user.groups if other_group != group]
        await message.answer(message='Кажется, произошла какая-то ошибка. Не могу найти расписание для твоей группы',
                             keyboard=custom_keyboard(buttons=buttons,
                                                      buttons_in_row=5))
