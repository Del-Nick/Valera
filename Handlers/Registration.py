import difflib

from Handlers.Keyboards import *
from Scripts.Arrays import groups
from Server.DB import User
from Config.Config import api

from vkbottle import Keyboard, Text
from vkbottle.bot import Message


async def registration(user: User, message: Message):
    match user.action.replace('registration_', ''):

        case 'first_message':
            await user.connection()
            await message.answer(
                f'Привет, {user.vk_name.split(" ")[0]}! Меня зовут Валера, я твой чат-бот. Если вдруг ты запутался и '
                f'не знаешь выход, просто позови меня по имени, и я тебя вытащу.')

            await message.answer(
                f'Давай немного познакомимся. Для полноценной работы мне необходимо знать твою группу. Напиши её, '
                f'пожалуйста. Если ты не студент физического факультета, нажми на кнопку.',
                keyboard=Keyboard(one_time=True).add(Text('Я не студент физфака'), color=KeyboardButtonColor.NEGATIVE))

            user.action = 'registration_add_group'

        case 'add_group':

            if message.text.lower() in groups:
                user.group = message.text.lower()
                user.action = 'registration_help'

                await message.answer(
                    f'Отлично, {user.vk_name.split(" ")[0]}! Я запомнил, что ты из группы {user.group}. Этот параметр '
                    f'можно будет изменить в настройках. Теперь я буду искать информацию для тебя персонально')
                await message.answer(
                    f'Хочешь пройти обучение?', keyboard=yes_no_keyboard())

            elif message.text == 'Я не студент физфака':
                await message.answer(f"Хорошо, {user.vk_name.split(' ')[0]}. Я запомнил, что ты не с физического "
                                     f"факультета. Пожалуйста, продублируй сообщение, чтобы мы его не "
                                     f"пропустили.\n\nP.s. Если кнопка была нажата по ошибке, ты всегда можешь "
                                     f"написать 'Я студент физфака' или 'Я студентка физфака', "
                                     f"чтобы зарегистрироваться.")
                user.action = 'not_student'

            else:
                await message.answer(
                    f'Не могу найти группу. Выбери на клавиатуре, если найдёшь подходящую',
                    keyboard=group_keyboard(difflib.get_close_matches(message.text.lower(), groups, n=5)))

                user.action = 'registration_error_group_adding_error'

        case 'error_group_adding_error':
            if message.text.lower() in groups:
                user.group = message.text.lower()
                user.action = 'registration_help'

                await message.answer(
                    f'Отлично, {user.vk_name.split(" ")[0]}! Я запомнил, что ты из группы {user.group}. Этот параметр '
                    f'можно будет изменить в настройках. Теперь я буду искать информацию для тебя персонально')
                await message.answer(
                    f'Хочешь пройти обучение?', keyboard=yes_no_keyboard())
            else:
                await message.answer('Я немного запутался. Уже зову на помощь админа')
                await api.messages.send(peer_id=2000000001, random_id=0,
                                        message=f'Пользователь {user.vk_name} не может правильно ввести группу. Срочно '
                                                f'требуется помощь. Уиуиуиуиуи 🚨🚨🚨')

        case 'help':
            match message.text:

                case 'Да':
                    await message.answer(
                        f'Пока обучение не доступно', keyboard=standard_keyboard(user))

                case _:
                    await message.answer(
                        f'Добро пожаловать в главное меню', keyboard=standard_keyboard(user))

            user.action = 'start_menu'

    await user.update()