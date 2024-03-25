import json
from datetime import datetime, timedelta
from Handlers.Keyboards import standard_keyboard


def weekday():
    return datetime.today().weekday()


def number_of_week():
    return datetime.today().isocalendar()[1]


async def schedule(info_bd, settings, message, group=None):
    if group is None:
        group = info_bd.group_user.split(', ')[0]

    with open('Scripts/Schedule.json', encoding='utf-8') as f:
        data = json.load(f)

    if group not in data.keys():
        return 'Что-то не наблюдаю расписания для этой группы &#128533;'
    else:
        data = data[group]

    number_of_week_var = number_of_week() - 34

    day = weekday()
    date = datetime.now()
    if day == 6:
        day = 0
        date += timedelta(days=1)
        number_of_week_var += 1
    elif datetime.now().strftime('%H:%M') > info_bd.time_new_schedule:
        if day == 5:
            day = 0
            date += timedelta(days=2)
            number_of_week_var += 1
        else:
            day += 1
            date += timedelta(days=1)

    answer = list(data.keys())[day].upper() + ', ' + date.strftime('%d.%m') + '\n\n'

    day = list(data.keys())[day]

    lessons_time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40', '18:55-20:30']

    num_of_lessons = 0
    if number_of_week_var % 2 != 0:
        for lesson in range(1, 7):
            temp = data[day][str(lesson)]["odd week"]
            if len(temp["lesson"]) > 2:
                num_of_lessons += 1
                if settings.full_schedule:
                    answer += f'{lessons_time[lesson - 1]}\n{temp["lesson"]} {temp["room"]}\n{temp["teacher"]}\n\n'
                else:
                    answer += f'{lessons_time[lesson - 1]}  {temp["lesson"]}  {temp["room"]}\n'
    else:
        for lesson in range(1, 7):
            temp = data[day][str(lesson)]["even week"]
            if len(temp["lesson"]) > 2:
                num_of_lessons += 1
                if settings.full_schedule:
                    answer += f'{lessons_time[lesson - 1]}\n{temp["lesson"]} {temp["room"]}\n{temp["teacher"]}\n\n'
                else:
                    answer += f'{lessons_time[lesson - 1]}  {temp["lesson"]}  {temp["room"]}\n'

    if num_of_lessons == 1:
        answer += '\nУ тебя 1 пара'
    elif num_of_lessons < 5:
        answer += f'\nУ тебя {num_of_lessons} пары'
    else:
        answer += f'\nУ тебя {num_of_lessons} пар'

    await message.answer(answer, keyboard=standard_keyboard(settings.headman, info_bd))


async def week_schedule(info_bd, settings, message, group=None):
    if group is None:
        group = info_bd.group_user.split(',')[0]

    with open('Scripts/Schedule.json', encoding='utf-8') as f:
        data = json.load(f)

    if group not in data.keys():
        return 'Что-то не наблюдаю расписания для этой группы &#128533;'
    else:
        data = data[group]

    number_of_week_var = number_of_week() - 34

    day = weekday()
    date = datetime.now()

    separator = '·'
    num_of_copies = 55

    next_week = False
    if day == 6:
        number_of_week_var += 1
        next_week = True
        answer = f'Следующая неделя № {number_of_week_var}\n\n'
    elif datetime.now().strftime('%H:%M') > info_bd.time_new_schedule:
        if day == 5:
            number_of_week_var += 1
            next_week = True
            answer = f'Следующая неделя № {number_of_week_var}\n\n'
        else:
            answer = f'Неделя № {number_of_week_var}\n\n'
    else:
        answer = f'Неделя № {number_of_week_var}\n\n'

    lessons_time = ['9:00-10:35', '10:50-12:25', '13:30-15:05', '15:20-16:55', '17:05-18:40', '18:55-20:30']

    if number_of_week_var % 2 != 0:
        for day_of_week in data.keys():
            if settings.full_schedule:
                answer += separator * num_of_copies + '\n\n'
            if next_week:
                answer += f'{list(data.keys()).index(day_of_week)+1}&#8419; ' + day_of_week.upper() + ', ' + (
                        date - timedelta(
                    days=date.weekday() - list(data.keys()).index(day_of_week) - 7)).strftime('%d.%m') + '\n\n'
            else:
                answer += f'{list(data.keys()).index(day_of_week)+1}&#8419; ' + day_of_week.upper() + ', ' + (
                        date - timedelta(days=date.weekday() - list(data.keys()).index(day_of_week))).strftime(
                    '%d.%m') + '\n\n'
            for lesson in range(1, 7):
                temp = data[day_of_week][str(lesson)]["odd week"]
                if len(temp["lesson"]) > 2:
                    if settings.full_schedule:
                        answer += f'{lessons_time[lesson - 1]}\n{temp["lesson"]} {temp["room"]}'
                        if len(temp["teacher"]) > 2:
                            answer += f'\n{temp["teacher"]}\n\n\n'
                        else:
                            answer += '\n\n'
                    else:
                        answer += f'{lessons_time[lesson - 1]}  {temp["lesson"]}  {temp["room"]}\n'

            if settings.full_schedule:
                answer = answer[:-1] + '\n\n'
            else:
                answer += '\n\n'

        await message.answer(answer, keyboard=standard_keyboard(settings.headman, info_bd))

    else:
        for day_of_week in data.keys():
            if settings.full_schedule:
                answer += separator * num_of_copies + '\n\n'
            if next_week:
                answer += f'{list(data.keys()).index(day_of_week)+1}&#8419; ' + day_of_week.upper() + ', ' + (
                        date - timedelta(days=date.weekday() - day - 7)).strftime('%d.%m') + '\n\n'
            else:
                answer += f'{list(data.keys()).index(day_of_week)+1}&#8419; ' + day_of_week.upper() + ', ' + (
                        date - timedelta(days=date.weekday() - day)).strftime('%d.%m') + '\n\n'
            for lesson in range(1, 7):
                temp = data[day_of_week][str(lesson)]["even week"]
                if len(temp["lesson"]) > 2:
                    if settings.full_schedule:
                        answer += f'{lessons_time[lesson - 1]}\n{temp["lesson"]} {temp["room"]}'
                        if len(temp["teacher"]) > 2:
                            answer += f'\n{temp["teacher"]}\n\n'
                        else:
                            answer += '\n\n'
                    else:
                        answer += f'{lessons_time[lesson - 1]}  {temp["lesson"]}  {temp["room"]}\n'

            if settings.full_schedule:
                answer = answer[:-1] + '\n\n'
            else:
                answer += '\n\n'

        await message.answer(answer, keyboard=standard_keyboard(settings.headman, info_bd))