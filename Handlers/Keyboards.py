from vkbottle import Keyboard, KeyboardButtonColor, Text
from Server.DB import User
import math


class UserKeyboards:

    @staticmethod
    def standard_keyboard(user: User):
        '''
            Это основная клавиатура главного меню
            :param user: класс пользователя со всей информацией о ней
            :return: Возвращает объект клавиатуры
            '''
        group = user.group.split(',')[0]

        keyboard = Keyboard()

        keyboard.add(Text('&#128466; ДЗ'), color=KeyboardButtonColor.POSITIVE) \
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

    @staticmethod
    def settings_keyboard(user: User):
        '''
        Клавиатура, которая появляется в настройках
        :param user: класс пользователя с данными из БД
        :return: объект клавиатуры
        '''
        keyboard = Keyboard(one_time=True)

        keyboard.add(Text(f'&#8987; Время: {user.schedule_next_day_after}'), color=KeyboardButtonColor.PRIMARY) \
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

    @staticmethod
    def group_keyboard(groups: list, enter_other_group: bool = True):
        '''
        Возвращает клавиатуру с возможными группами при неправильном вводе
        :param enter_other_group: По умолчанию истина. Если ложь, кнопка 'Нет нужной группы' исчезает
        :param groups: список наиболее подходящих групп
        :return: Возвращает объект клавиатуры
        '''
        keyboard = Keyboard(inline=True)

        for group in groups:
            keyboard.add(Text(group))

        if enter_other_group:
            keyboard.row().add(Text('Нет нужной группы'))

        keyboard.row().add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE)

        return keyboard

    @staticmethod
    def yes_no_keyboard():
        '''
        Простая да/нет клавиатура
        :return: Возвращает объект клавиатуры
        '''
        keyboard = Keyboard(inline=True)

        keyboard.add(Text('Нет'), color=KeyboardButtonColor.NEGATIVE) \
            .add(Text('Да'), color=KeyboardButtonColor.POSITIVE)

        return keyboard

    @staticmethod
    def after_schedule_keyboard(user: User, day: int = None, week_schedule: bool = False, parity: str = None):
        '''
        Это inline клавиатура, которая появляется после вызова расписания. Содержит выбор дня недели и других групп
        :param user: класс пользователя с данными из БД
        :param day: Порядковый номер дня недели от 0
        :param week_schedule: Определяет, вызывалось расписание на неделю или нет
        :param parity: Чётность недели. Принимает два параметра 'odd' и 'even'
        :return: объект клавиатуры
        '''
        keyboard = Keyboard(inline=True)

        if week_schedule:
            if parity == 'odd':
                keyboard.add(Text('Нечётная'))
            else:
                keyboard.add(Text('Чётная'))

        else:
            # Если пользователь запрашивал расписание на день, то добавляем в клавиатуру варианты других дней
            if 'after_schedule' in user.action:
                weekdays = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ']
                weekdays.pop(day)

                for i, weekday in enumerate(weekdays):
                    keyboard.add(Text(weekday))

        keyboard.row()

        if len(user.group.split(',')) > 1:
            group_for_delete = user.action.split('_')[-1]
            print('group_for_delete', group_for_delete)
            groups = user.group.split(',')

            if group_for_delete in groups:
                groups.remove(group_for_delete)

            for group in groups:
                keyboard.add(Text(group))
            keyboard.row()

        keyboard.add(Text('Ввести другую группу')).row()

        keyboard.add(Text('Сообщить об ошибке'))

        return keyboard

    @staticmethod
    def cancel_keyboard():
        '''
        Просто кнопка отмены
        :return: объект клавиатуры
        '''
        return Keyboard().add(Text('Отмена'), color=KeyboardButtonColor.NEGATIVE)
