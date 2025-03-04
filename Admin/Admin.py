import aiohttp
from vkbottle.bot import Message

from Config.Config import doc_uploader
from Handlers.Keyboards import standard_keyboard, cancel_keyboard
from Server.Core import BooksDB, DB
from Server.Models import User


async def admin_handler(admin: User, message: Message):
    if admin.action == 'admin_get_book':
        if message.text == 'Отмена':
            await message.answer(f'Возвращаюсь в главное меню',
                                 keyboard=standard_keyboard(admin))
            admin.action = 'start'

        else:
            try:
                course, semester, subject = message.text.split(' -')
                books = await BooksDB.select_books(course)

                if message.attachments[0]:
                    if message.attachments[0].doc:
                        filename = message.attachments[0].doc.title

                        async with aiohttp.ClientSession() as session:
                            async with session.get(message.attachments[0].doc.url) as response:
                                result = await response.read()

                        doc = await doc_uploader.upload(title=filename, file_source=result, peer_id=message.peer_id)

                        num_file = None

                        for num, book in enumerate(books.books[f'{semester} семестр'][subject]):
                            if book['name'] == filename:
                                num_file = num
                                break

                        if num_file is not None:
                            books.books[f'{semester} семестр'][subject][num_file]['vk_file_id'] = doc
                            await BooksDB.update_books(books)

                            await message.answer(f'Учебник: {filename}\n\n'
                                                 f'Сохранил учебник для {course} курса, {semester} семестра по предмету '
                                                 f'{subject}',
                                                 attachment=doc,
                                                 keyboard=standard_keyboard(admin))
                            admin.action = 'start'

                        else:
                            books_str = '\n'.join([book['name'] for book in books.books[f'{semester} семестр'][subject]])
                            await message.answer(f'Не смог найти такой учебник в своей базе. Вот названия учебников, '
                                                 f'которые у меня есть:\n\n{books_str}',
                                                 keyboard=cancel_keyboard())

                else:
                    await message.answer(f'Ты забыл прикрепить файл',
                                         keyboard=cancel_keyboard())

            except ValueError:
                photo = message.attachments[0].photo
                await message.answer(f'photo{photo.owner_id}_{photo.id}_{photo.access_key}',
                                     keyboard=standard_keyboard(admin))
                await message.answer('Вводи по образцу: "курс -семестр -предмет"',
                                     keyboard=cancel_keyboard())
