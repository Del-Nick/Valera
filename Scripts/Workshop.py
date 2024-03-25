import os
import json
import datetime
import requests
from vkbottle import Keyboard, KeyboardButtonColor, Text
from Handlers.Keyboards import custom_keyboard
from Config.Config import owner_id, app_token
from Scripts.Arrays import workshop_rooms

first_sem = ['101', '102', '103', '104', '105', '106', '108', '110', '112', '114', '116', '117', '117. Рекомендации',
             '118', '119', '120', '121', '122', '123', '124', '125', '126', '127']
second_sem = ['201', '202', '204', '205', '206', '207', '208', '210', '218', '219', '219m', '226', '227', '228', '230',
              '232', '233', '234', '238', '240', '240б']
third_sem = ['301', '302', '304', '305', '305А', '307', '308', '308М', '309', '319', '322', '323', '324', '325', '336',
             '337', '338', '339', '340']
forth_sem = ['128', '132', '132А', '135', '136', '140', '142', '147', '152', '169', '401', '403', '408', '409', '410',
             '411', '412', '413', '419']


async def workshop(vk_id: int, info_bd, message):
    group = info_bd.group_user.split(', ')[0]
    path = f'Files/Workshops/{group}.json'

    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            schedule_workshop = json.load(f)

        answer = ''

        if str(id) in schedule_workshop.keys():
            for date in schedule_workshop[str(id)].keys():
                if schedule_workshop[str(id)][date]['status'] == 'Not started':
                    answer += f'&#128198; {date}{"˲" * 10}' \
                              f'{schedule_workshop[str(id)][date]["num"]}{"˲" * 3}&#127770;\n\n'
                elif schedule_workshop[str(id)][date]['status'] == 'Not passed':
                    answer += f'&#128198; {date}{"˲" * 10}' \
                              f'{schedule_workshop[str(id)][date]["num"]}{"˲" * 3}&#127771;\n\n'
                elif schedule_workshop[str(id)][date]['status'] == 'Passed':
                    answer += f'&#128198; {date}{"˲" * 10}' \
                              f'{schedule_workshop[str(id)][date]["num"]}{"˲" * 3}&#127773;\n\n'
                else:
                    answer += f'&#128198; {date}{"˲" * 10}' \
                              f'{schedule_workshop[str(id)][date]["num"]}\n\n'
            await message.answer(answer)
        else:
            await message.answer('Не смог найти тебя в таблице &#128532;')
    else:
        await message.answer('Староста твоей группы ещё не добавил расписание практикумов')

    if group[0] == '1':
        if datetime.datetime.today().month > 8:
            await message.answer(
                'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                keyboard=custom_keyboard(first_sem))
        else:
            await message.answer(
                'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                keyboard=custom_keyboard(second_sem))
    elif group[0] == '2':
        if datetime.datetime.today().month > 8:
            await message.answer(
                'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                keyboard=custom_keyboard(third_sem))
        else:
            await message.answer(
                'Выбери или введи номер общего физического практикума, и я пришлю тебе методичку',
                keyboard=custom_keyboard(forth_sem))
    else:
        await message.answer('Введи номер общего физического практикума, и я пришлю тебе методичку',
                             keyboard=Keyboard(one_time=True).add(Text('Отмена'),
                                                                  color=KeyboardButtonColor.NEGATIVE))


def workshop_manual(message):
    url = 'https://api.vk.com/method/docs.get'
    data = {
        'owner_id': owner_id,
        'access_token': app_token,
        'v': '5.131'
    }
    response = requests.get(url, params=data)
    response = response.json()

    if 'error' in response.keys():
        print(response)
        return 'Не смог подклюситься к серверу. Попробуй ещё раз, пожалуйста', None

    names = []

    for i in range(len(response['response']['items'])):
        names.append(response['response']['items'][i]['title'])

    link = ''
    num = 0
    try:
        while True:
            if response['response']['items'][num]['title'] == message.text:
                break
            num += 1

        doc_id = response['response']['items'][num]['id']
        link = f'doc{owner_id}_{doc_id}'
    except Exception as Ex:
        print(Ex)

    if 'doc' in link:
        return f'Кабинет: {search_workshop_room(message.text)}. Держи', link
    else:
        return 'Не знаю, что со мной сегодня. Не могу найти методичку..', None


def search_workshop_room(number):
    try:
        for key in workshop_rooms.keys():
            if number in workshop_rooms[key]:
                break
        return key
    except:
        return 'Не найден'


