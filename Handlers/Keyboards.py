from vkbottle import Keyboard, KeyboardButtonColor, Text
from Server.DB import User
import math


def standard_keyboard(user: User):
    '''
    Это основная клавиатура главного меню
    :param user: класс пользователя со всей информацией о ней
    :return: Возвращает объект клавиатуры
    '''
    group = user.group.split(',')[0]

    keyboard = Keyboard() \
        .add(Text('&#128466; ДЗ'), color=KeyboardButtonColor.POSITIVE) \
        .add(Text('&#128218; Учебники'), color=KeyboardButtonColor.POSITIVE)

    if group:
        if len(group) == 3 and int(group[0]) < 3:
            keyboard.add(Text('&#128300; Праки'), color=KeyboardButtonColor.POSITIVE)

    keyboard.row() \
        .add(Text('&#128198; Расписание'), color=KeyboardButtonColor.POSITIVE) \
        .add(Text('7&#8419;&#128198; На неделю'), color=KeyboardButtonColor.POSITIVE) \
        .row() \
        .add(Text('&#9881; Настройки'))

    if user.headman:
        keyboard.add(Text('&#128526; Cтароста Mode'))

    if user.admin:
        keyboard.add(Text('Админ'))

    return keyboard


def settings_keyboard(user: User):
    keyboard = Keyboard() \
        .add(Text(f'&#8987; Время: {user.schedule_next_day_after}'), color=KeyboardButtonColor.PRIMARY) \
        .add(Text('&#128256; Сменить группу'), color=KeyboardButtonColor.PRIMARY) \
        .row() \
        .add(Text('Удалить группу'), color=KeyboardButtonColor.NEGATIVE) \
        .add(Text('Добавить группу'), color=KeyboardButtonColor.POSITIVE) \
        .row()

    if user.full_schedule:
        keyboard.add(Text('Полное расписание: &#9989;'), color=KeyboardButtonColor.POSITIVE).row()
    else:
        keyboard.add(Text('Полное расписание: &#9745;'), color=KeyboardButtonColor.SECONDARY).row()

    if user.notifications:
        keyboard.add(Text('Уведомления: &#9989;'), color=KeyboardButtonColor.POSITIVE).row()
    else:
        keyboard.add(Text('Уведомления: &#9745;'), color=KeyboardButtonColor.SECONDARY).row()

    if user.schedule_seller:
        keyboard.add(Text('Присылать расписание: &#9989;'), color=KeyboardButtonColor.POSITIVE).row()
    else:
        keyboard.add(Text('Присылать расписание: &#9745;'), color=KeyboardButtonColor.SECONDARY).row()

    keyboard.add(Text('&#10067; Помощь')) \
        .add(Text('&#128281; Вернуться назад'))

    return keyboard


def group_keyboard(id: int, groups: str):
    groups = groups.split(', ')
    keyboard = Keyboard(one_time=True)
    for group in range(len(groups)):
        keyboard.add(Text(f'{groups[group]}'))

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


def group_keyboard(groups: list):
    '''
    Возвращает клавиатуру с возможными группами при неправильном вводе
    :param groups: список наиболее подходящих групп
    :return: Возвращает объект клавиатуры
    '''
    keyboard = Keyboard(inline=True)
    for group in groups:
        keyboard.add(Text(group))

    keyboard.row().add(Text('Нет нужной группы'))

    return keyboard


def yes_no_keyboard():
    '''
    Простая да/нет клавиатура
    :return: Возвращает объект клавиатуры
    '''
    keyboard = Keyboard(inline=True)

    keyboard.add(Text('Нет'), color=KeyboardButtonColor.NEGATIVE)\
        .add(Text('Да'), color=KeyboardButtonColor.POSITIVE)

    return keyboard


def after_schedule_keyboard(user: User):
    keyboard = Keyboard(inline=True)

    weekdays = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']

    for i, weekday in enumerate(weekdays):
        keyboard.add(Text(weekday))
        if i == 2:
            keyboard.row()

    keyboard.row()

    if len(user.group.split(',')) > 1:
        groups = user.group.split(',')
        for group in groups:
            keyboard.add(Text(group))
        keyboard.row()

    keyboard.add(Text('Сообщить об ошибке'))

    return keyboard


def custom_keyboard(buttons):
    keyboard = Keyboard(one_time=True)
    koef = int(5 * math.exp(-0.05 * len(str(max(buttons)))))
    for button in range(len(buttons)):
        keyboard.add(Text('%s' % buttons[button]))

        if (button + 1) % koef == 0:
            keyboard.row()
    keyboard.add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE)
    return keyboard
