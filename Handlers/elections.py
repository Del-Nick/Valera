from typing import Type

from vkbottle import Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Message

from Handlers.Keyboards import yes_no_keyboard
from Scripts.Arrays import GROUPS
from Server.Core import ElectionsDB
from Server.Models import User, Elections


class Keyboards:
    @staticmethod
    def one_button_keyboard(button: str = None) -> Keyboard:
        keyboard = Keyboard(inline=True)

        if button:
            keyboard.add(Text(button), color=KeyboardButtonColor.PRIMARY)
        keyboard.add(Text('Назад'), color=KeyboardButtonColor.SECONDARY)

        return keyboard


kboard = Keyboards()


async def elections_handler(user: User, message: Message):
    if user.action == 'elections_start':
        await message.answer('Ты можешь оставить свой голос на выборах в Студенческий Совет. Но для начала нам нужно '
                             'задать тебе пару вопросов, которые позволят избежать голосования два и более раз. Помни, '
                             'что возможности исправить голос у тебя не будет. Введи свою настоящую группу?',
                             keyboard=kboard.one_button_keyboard(user.groups[0]))
        user.action = 'elections_get_group'
        elections = Elections(vk_id=user.VkID)
        await ElectionsDB.insert_elections(elections)

    elif user.action == 'elections_get_group':
        elections = await ElectionsDB.select_elections(user.VkID)

        if message.text.lower() in GROUPS:
            await message.answer('Отлично. Теперь мне нужно узнать твои полные фамилию, имя и отчество. Напиши их в '
                                 'формате:\n\n'
                                 'Иванов Иван Иванович')
            elections.group = message.text.lower()
            await ElectionsDB.update_elections(elections)
            user.action = 'elections_get_fio'

        else:
            await message.answer('Я не смог найти группу. Проверь правильность и попробуй ещё раз. Если не получится, '
                                 'свяжись с представителями Студсовета',
                                 keyboard=kboard.one_button_keyboard())

    elif user.action == 'elections_get_fio':
        elections = await ElectionsDB.select_elections(user.VkID)

        elections.fio = message.text
        await message.answer(f'Супер, {message.text.split()[1]}. Перед тобой анкеты претендентов. Ознакомься с ними и '
                             f'напиши мне номер кандидата, за которого хочешь проголосовать',
                             keyboard=kboard.one_button_keyboard())