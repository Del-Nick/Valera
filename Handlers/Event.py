import asyncio
import random
from datetime import datetime

from Handlers.Keyboards import standard_keyboard
from Server.Core import QuizUserDB, QuizDB
from Server.Models import User, Quiz, QuizUser
from vkbottle.bot import Message
from vkbottle import Keyboard, KeyboardButtonColor, Text


class Keyboards:
    @staticmethod
    def main_keyboard():
        keyboard = Keyboard(one_time=True) \
            .add(Text('🤯  КВИЗ  🤯'), color=KeyboardButtonColor.POSITIVE) \
            .row() \
            .add(Text('Назад'), color=KeyboardButtonColor.SECONDARY)

        return keyboard

    @staticmethod
    def start_quiz_keyboard():
        keyboard = Keyboard(one_time=True) \
            .add(Text('Конечно!'), color=KeyboardButtonColor.POSITIVE) \
            .row() \
            .add(Text('Назад'), color=KeyboardButtonColor.SECONDARY)

        return keyboard

    @staticmethod
    def quiz_keyboard(question: Quiz):
        keyboard = Keyboard(one_time=True)

        vars = question.variants
        random.shuffle(vars)

        for i, var in enumerate(vars):
            keyboard.add(Text(var.replace('*', '')), color=KeyboardButtonColor.PRIMARY)

            if i < len(vars) - 1:
                keyboard.row()

        return keyboard


wrong_answers = ['Неверно, но не отчаивайся: каждая попытка — это маленькое приключение!',
                 'Неверно, но это просто ещё одна возможность узнать что-то новое',
                 'Не совсем так',
                 'Ну, почти']

true_answers = ['Да, в точку!',
                'Зришь в корень!',
                'Кто понял жизнь, тот не спешит']

event_schedule = ('Приглашаем вас посетить мероприятия, приуроченные ко Дню российской науки.\n\n'
                  ''
                  '          7 февраля:\n\n'
                  '12³⁰ - 14⁰⁰ — круглый стол с учёными физфака "Физиком становятся" в СФА\n'
                  '14⁰⁰ - 15²⁰ — Мастер-класс "Оформи стендовый доклад", физическая настольная '
                  'игра "AliaScience" и кофе-брейк в холле ЦФА\n'
                  '15²⁰ - 16⁵⁵ — Лекция от "Лаборатории Касперского" в СФА\n\n\n'
                  ''
                  '          12 февраля:\n\n'
                  '🔹"Научный бой" между факультетами в коворкинге 1 ГУМа\n'
                  '🔹Экскурсии в научно-исследовательские центры и компании - даты уточняются\n'
                  '🔹Посещение лабораторий и кафедр физического факультета - даты уточняются')


async def event_handler(user: User, message: Message):
    if user.action == 'event':
        quiz_user = await QuizUserDB.select(user_id=user.ID)

        if 'квиз' in message.text.lower():
            if quiz_user:
                await message.answer(message=f'Поздравляю! Твой результат {quiz_user.count_true_answers} из 11 '
                                             f'вопросов! На прохождение ушло '
                                             f'{(quiz_user.end_datetime - quiz_user.start_datetime).total_seconds():.1f} c')
                await message.answer(message=event_schedule,
                                     keyboard=Keyboards.main_keyboard())
            else:
                await message.answer(
                    message='Рады приветствовать тебя на этой викторине. Впереди тебя ждут 11 вопросов из разных '
                            'областей. \n\n'
                            'За хорошие ответы ты получишь призы, но играй честно, не подглядывай и не говори ответы другим '
                            'участникам. Давай не портить впечатления от игры.\n\n'
                            ''
                            'Небольшое уточнение. После начала викторины ты не сможешь вернуться в основное меню, пока не '
                            'закончишь её. Начинаем?',
                    keyboard=Keyboards.start_quiz_keyboard())
                user.action = 'event_quiz'

        else:
            user.action = 'start_menu'
            await message.answer(message='Вжух! Мы в главном меню',
                                 keyboard=standard_keyboard(user=user))

    elif user.action == 'event_quiz':
        if message.text == 'Конечно!':
            user.action = 'event_quiz_started?num=1'
            question = await QuizDB.select(num=1)
            await message.answer(message=question.question,
                                 keyboard=Keyboards.quiz_keyboard(question))
            await QuizUserDB.insert(QuizUser(user_id=user.ID))

        else:
            user.action = 'event'
            await message.answer(message=event_schedule,
                                 keyboard=Keyboards.main_keyboard())

    elif user.action.startswith('event_quiz_started'):
        num = int(user.action.replace('event_quiz_started?num=', ''))
        question = await QuizDB.select(num=num)
        quiz_user = await QuizUserDB.select(user_id=user.ID)

        if message.text == question.answer:
            await message.answer(message=random.choice(true_answers))
            quiz_user.count_true_answers += 1

        else:
            await message.answer(message=random.choice(wrong_answers))

        await message.answer(message=f'Правильный ответ: {question.answer}')

        if num == 11:
            quiz_user.end_datetime = datetime.now()

        if question.desc:
            pause = len(question.desc) // 24
            await message.answer(message=f'{question.desc}\n\n'
                                         f'Следующий вопрос через {pause} с')

            await asyncio.sleep(pause)

        if num < 11:
            question = await QuizDB.select(num=num + 1)
            await message.answer(message=question.question.replace('*', ''),
                                 keyboard=Keyboards.quiz_keyboard(question))
            user.action = f'event_quiz_started?num={num + 1}'

        else:
            await message.answer(message=f'Поздравляю! Ты завершаешь викторину, ответив верно на '
                                         f'{quiz_user.count_true_answers} из 11 вопросов! На прохождение ушло '
                                         f'{(quiz_user.end_datetime - quiz_user.start_datetime).total_seconds():.1f} c')
            user.action = 'event'
            await message.answer(message=event_schedule,
                                 keyboard=Keyboards.main_keyboard())

        await QuizUserDB.update(quiz_user)
