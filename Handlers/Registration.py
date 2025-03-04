import difflib
import sys
from loguru import logger

from vkbottle import Keyboard, Text
from vkbottle.bot import Message

from Handlers.Keyboards import *
from Scripts.Arrays import GROUPS
from Server.Models import User
from Server.Core import DB
from Config.Config import api, GETTING_ERROR

logger.remove()
logger.add(sys.stderr, level="INFO")


async def registration(user: User, message: Message) -> User:
    if user.action == 'registration_first_message':
        await message.answer(
            f'Привет, {user.VkFirstName}! Меня зовут Валера, я твой чат-бот. Если вдруг ты запутался и '
            f'не знаешь выход, просто позови меня по имени, и я тебя вытащу.')

        await message.answer(
            f'Если у тебя уже есть регистрация через Telegram, напиши мне свой ник, чтобы '
            f'я синхронизировал настройки. Если нет, заверши регистрацию здесь, а потом укажи свой VkID в Telegram',
            keyboard=Keyboard(one_time=True)
            .add(Text('Нет регистрации в Telegram'),
                 color=KeyboardButtonColor.NEGATIVE)
            .add(Text('Выборы в Студсовет'),
                 color=KeyboardButtonColor.PRIMARY))

        user.action = 'registration_get_tg_name'

    elif user.action == 'registration_get_tg_name':
        if message.text == 'Нет регистрации в Telegram':
            user.action = 'registration_add_group'
            await message.answer(
                f'Давай немного познакомимся. Для полноценной работы мне необходимо знать твою группу. Напиши её, '
                f'пожалуйста. Если ты не студент физического факультета, нажми на кнопку.',
                keyboard=Keyboard(one_time=True).add(Text('Я не студент физфака'),
                                                     color=KeyboardButtonColor.NEGATIVE))
        else:
            if await DB.check_user_exists(TgName=message.text.replace('@', '')):
                await DB.merge_records(vk_user=user, tg_name=message.text.replace('@', ''))
                user = await DB.select_user(TgName=message.text.replace('@', ''))

                if user.groups:
                    await message.answer(
                        f'Добро пожаловать в главное меню', keyboard=standard_keyboard(user))
                    user.action = 'start_menu'
                else:
                    await message.answer('Напиши мне свою учебную группу')
                    user.action = 'registration_add_group'

                await DB.update_user(user)

            else:
                await message.answer('Кажется, я впервые вижу такой ник. Ничего страшного, можешь прикрепить свой '
                                     'аккаунт ВКонтакте, когда будешь в Telegram. Напиши мне свою учебную группу')

                user.action = 'registration_add_group'
                await DB.update_user(user)

    elif user.action == 'registration_add_group':
        if message.text.lower() in GROUPS:
            user.groups = [message.text.lower()]
            user.action = 'registration_help'

            await message.answer(
                f'Отлично, {user.VkFirstName}! Я запомнил, что ты из группы {user.groups[0]}. Этот параметр '
                f'можно будет изменить в настройках. Теперь я буду искать информацию для тебя персонально')

            if not user.TgID:
                await message.answer('Кстати, прикреплю ссылку на Telegram t.me/studsovet_ff_bot. Можешь указать '
                                     'там свой ID или ник ВКонтакте, все настройки синхорнизируются',
                                     keyboard=standard_keyboard(user))

            await message.answer('Полезный совет\n\n'
                                 'Чтобы узнать, где находится кабинет, просто напиши мне его в любой форме, к примеру, '
                                 '5-47, 547, 5 47, столовая или даже учебная часть',
                                 keyboard=standard_keyboard(user))
            user.action = 'start_menu'

        elif message.text == 'Я не студент физфака':
            await message.answer(f"Хорошо, {user.VkFirstName}. Я запомнил, что ты не с физического "
                                 f"факультета. Пожалуйста, продублируй сообщение, чтобы мы его не "
                                 f"пропустили.\n\nP.s. Если кнопка была нажата по ошибке, ты всегда можешь "
                                 f"написать 'Я студент физфака' или 'Я студентка физфака', "
                                 f"чтобы зарегистрироваться.")
            user.action = 'registration_not_student'

        else:
            await message.answer(
                f'Не могу найти группу. Выбери на клавиатуре, если найдёшь подходящую',
                keyboard=group_keyboard(difflib.get_close_matches(message.text.lower(), GROUPS, n=5), cancel=False))

            user.action = 'registration_error_group_adding_error'

    elif user.action.startswith('registration_error_group_adding_error'):
        if message.text.lower() in GROUPS:
            # Если alert уже был отправлен админу, сообщаем, что всё ок
            if 'alert_sent' in user.action:
                await api.messages.send(peer_id=2000000001, random_id=0,
                                        message=f'Пользователь {user.VkFirstName} {user.VkLastName} всё-таки смог '
                                                f'ввести группу самостоятельно. Всем спасибо. Расходимся')

            user.groups = [message.text.lower()]
            user.action = 'registration_help'

            await message.answer(
                f'Отлично, {user.VkFirstName}! Я запомнил, что ты из группы {user.groups[0]}. Этот параметр '
                f'можно будет изменить в настройках. Теперь я буду искать информацию для тебя персонально',
                keyboard=standard_keyboard(user))

        else:
            if message.text == 'Нет нужной группы':
                await message.answer(
                    'Я всё ещё не могу распознать группу, но уже отправил сигнал тревоги админу. '
                    'Ты можешь подождать или попробовать ещё раз')
            else:
                await message.answer(
                    'Я всё ещё не могу распознать группу, но уже отправил сигнал тревоги админу. '
                    'Ты можешь подождать или попробовать ещё раз',
                    keyboard=group_keyboard(difflib.get_close_matches(message.text.lower(), GROUPS, n=5),
                                            cancel=False))
            if 'alert_sent' not in user.action:
                user.action = 'registration_error_group_adding_error_alert_sent'
                if GETTING_ERROR:
                    await api.messages.send(peer_id=2000000001, random_id=0,
                                            message=f'Пользователь {user.VkFirstName} {user.VkLastName} '
                                                    f'не может правильно ввести группу. Срочно требуется помощь. '
                                                    f'Уиуиуиуиуи 🚨🚨🚨\n\n'
                                                    f'Ссылка на переписку: https://vk.com/gim34300772?sel={user.VkID}')

    elif user.action.startswith('registration_help'):
        match message.text:
            case 'Да':
                await message.answer(
                    f'Пока обучение не доступно', keyboard=standard_keyboard(user))

            case _:
                await message.answer(
                    f'Добро пожаловать в главное меню', keyboard=standard_keyboard(user))

        user.action = 'start_menu'

    elif user.action.startswith('registration_not_student'):
        if message.text == 'Я студент физфака' or message.text == 'Я студентка физфака':
            await message.answer('Напиши мне свою учебную группу')
            user.action = 'registration_add_group'
