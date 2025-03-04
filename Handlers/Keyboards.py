import datetime
import json
from pprint import pprint

from vkbottle import Keyboard, KeyboardButtonColor, Text
from Server.Models import User
import math


def standard_keyboard(user: User):
    """
    Это основная клавиатура главного меню
    :param user: класс пользователя со всей информацией о ней
    :return: Возвращает объект клавиатуры
    """
    group = user.groups[0]

    keyboard = Keyboard(one_time=True) \
        .add(Text('&#128466; ДЗ'), color=KeyboardButtonColor.POSITIVE) \
        .add(Text('&#128218; Учебники'), color=KeyboardButtonColor.POSITIVE)

    if group:
        if len(group) == 3 and int(group[0]) < 3:
            keyboard.add(Text('&#128300; Праки'), color=KeyboardButtonColor.POSITIVE)

    # .add(Text('7&#8419;&#128198; На неделю'), color=KeyboardButtonColor.POSITIVE) \
    keyboard.row() \
        .add(Text('&#128198; Расписание'), color=KeyboardButtonColor.POSITIVE) \
        .row() \
        .add(Text('&#9881; Настройки'))

    end_voting = datetime.datetime(2024, 11, 26)
    if datetime.datetime.now() < end_voting:
        keyboard.row().add(Text('Выборы в Студсовет'), color=KeyboardButtonColor.PRIMARY)

    if user.settings.headman:
        keyboard.row().add(Text('&#128526; Cтароста Mode'))

    if user.settings.admin:
        keyboard.add(Text('Панель админа'))

    return keyboard


def settings_keyboard(user: User):
    keyboard = Keyboard(one_time=True) \
        .add(Text(f'&#8987; Время: {user.settings.tomorrow_schedule_after.strftime("%H:%M")}'),
             color=KeyboardButtonColor.PRIMARY) \
        .add(Text('&#128256; Сменить группу'), color=KeyboardButtonColor.PRIMARY) \
        .row() \
        .add(Text('Удалить группу'), color=KeyboardButtonColor.NEGATIVE) \
        .add(Text('Добавить группу'), color=KeyboardButtonColor.POSITIVE) \
        .row()

    if user.settings.full_schedule:
        keyboard.add(Text('Всё расписание: &#9989;'), color=KeyboardButtonColor.POSITIVE)
    else:
        keyboard.add(Text('Всё расписание: &#9745;'), color=KeyboardButtonColor.SECONDARY)

    if user.settings.notifications:
        keyboard.add(Text('Уведомления: &#9989;'), color=KeyboardButtonColor.POSITIVE).row()
    else:
        keyboard.add(Text('Уведомления: &#9745;'), color=KeyboardButtonColor.SECONDARY).row()

    # if user.settings.schedule_seller:
    #     keyboard.add(Text('Send Schedule: &#9989;'), color=KeyboardButtonColor.POSITIVE).row()
    # else:
    #     keyboard.add(Text('Send Schedule: &#9745;'), color=KeyboardButtonColor.SECONDARY).row()

    keyboard.add(Text('&#10067; Помощь')) \
        .add(Text('&#128281; Вернуться назад'))

    return keyboard


def subjects_keyboard(buttons, info_vk, info_bd, headman: bool = False):
    keyboard = Keyboard(one_time=True)
    temp = False
    for button in range(len(buttons)):
        temp = False
        keyboard.add(Text(f'{buttons[button]}'), color=KeyboardButtonColor.PRIMARY)
        if (button + 1) % 2 == 0:
            keyboard.row()
            temp = True

    if info_bd.action != 'Headman_mode':
        if not temp:
            keyboard.row()
        keyboard.add(Text('Вернуться в главное меню'))

    if headman and info_bd.action == 'Headman_mode':
        if not temp:
            keyboard.row()

        keyboard.add(Text('Добавить предмет'), color=KeyboardButtonColor.POSITIVE) \
            .row() \
            .add(Text('Удалить предмет'), color=KeyboardButtonColor.NEGATIVE) \
            .row() \
            .add(Text('Вернуться в меню старосты'), color=KeyboardButtonColor.SECONDARY)

    return keyboard


def headman_keyboard(action=''):
    if action == 'ДЗ':
        buttons = ['Добавить ДЗ', 'Удалить ДЗ', 'Вернуться к списку предметов', 'NEGATIVE']
    elif action == 'Учебник':
        buttons = ['Добавить учебник', 'Удалить учебник', 'Вернуться в меню старосты', 'NEGATIVE']
    elif action == 'Сессия':
        buttons = ['Добавить зачёт/экзамен', 'Удалить зачёт/экзамен', 'Вернуться в меню старосты', 'NEGATIVE']
    else:
        buttons = ['Редактировать учебники', 'Редактировать ДЗ', 'Вернуться в главное меню', '']

    keyboard = Keyboard(one_time=True)
    for i in range(len(buttons) - 2):
        if i == 1:
            if buttons[len(buttons) - 1] == 'NEGATIVE':
                keyboard.add(Text('%s' % buttons[i]), color=KeyboardButtonColor.NEGATIVE).row()
            else:
                keyboard.add(Text('%s' % buttons[i]), color=KeyboardButtonColor.POSITIVE).row()
        else:
            keyboard.add(Text('%s' % buttons[i]), color=KeyboardButtonColor.POSITIVE).row()

    keyboard.add(Text('%s' % buttons[len(buttons) - 2]), color=KeyboardButtonColor.SECONDARY)
    return keyboard


def group_keyboard(groups: list, enter_other_group: bool = True, cancel: bool = True):
    '''
    Возвращает клавиатуру с возможными группами при неправильном вводе
    :param enter_other_group: По умолчанию истина. Если ложь, кнопка 'Нет нужной группы исчезает'
    :param groups: список наиболее подходящих групп
    :return: Возвращает объект клавиатуры
    '''
    keyboard = Keyboard(inline=True)
    for group in groups:
        keyboard.add(Text(group))

    if enter_other_group:
        keyboard.row().add(Text('Нет нужной группы'))

    if cancel:
        keyboard.row().add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE)

    return keyboard


def yes_no_keyboard():
    '''
    Простая да/нет клавиатура
    :return: Возвращает объект клавиатуры
    '''
    keyboard = Keyboard(inline=True)

    keyboard.add(Text('Нет'), color=KeyboardButtonColor.NEGATIVE) \
        .add(Text('Да'), color=KeyboardButtonColor.POSITIVE)

    return keyboard


def after_schedule_keyboard(user: User, group: str, day: int = None):
    keyboard = Keyboard(inline=True)

    if day is not None:
        weekdays = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']
        weekdays.pop(day)

        for i, weekday in enumerate(weekdays):
            keyboard.add(Text(weekday))

        keyboard.row()

    if len(user.groups) > 1:
        count_groups = 0
        for user_group in user.groups:
            if user_group != group:
                keyboard.add(Text(user_group))
                count_groups += 1

            if count_groups == 2:
                break

        keyboard.row()

    keyboard.add(Text('Ввести другую группу'))

    keyboard.row().add(Text('Сообщить об ошибке')).row().add(Text('Назад'))

    return keyboard


def custom_keyboard(buttons: list[str], buttons_in_row: int = 2):
    keyboard = Keyboard(one_time=True)

    for num, button in enumerate(buttons):
        keyboard.add(Text(button), color=KeyboardButtonColor.PRIMARY)

        if num % buttons_in_row == 1 and num != len(buttons) - 1:
            keyboard.row()

    keyboard.row().add(Text('Назад'))

    return keyboard


def cancel_keyboard():
    return Keyboard().add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE)


def empty_keyboad():
    return Keyboard
