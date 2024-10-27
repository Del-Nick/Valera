import asyncio
import datetime
from random import randint

from vkbottle.bot import Message

from sqlalchemy import select, delete, text
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from Config.Config import global_settings, bot
from Server.Models import Base, User, Settings, Books, Homeworks, Workshops, Elections
from Scripts.Others import get_sex_of_person_by_name


engine = create_async_engine(url=global_settings.DATABASE_URL_asyncpg,
                             echo=False)
session_factory = async_sessionmaker(engine)


class DB:
    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            # await conn.run_sync(DeclarativeBase.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def select_manager(message: Message):
        user = await DB.select_user(VkID=message.from_id)

        if not user:
            vk_info = (await bot.api.users.get(message.from_id))[0]
            user = User(VkID=vk_info.id, VkFirstName=vk_info.first_name, VkLastName=vk_info.last_name,
                        sex=get_sex_of_person_by_name(vk_info.first_name))

            user.action = 'registration_first_message'
            settings = Settings(ID=user.ID)
            user.settings = settings
            await DB.insert_user(user)

            user = await DB.select_user(VkID=message.from_id)

        return user

    @staticmethod
    async def insert_user(user: User):
        async with session_factory() as session:
            session.add(user)
            await session.flush()

            session.add(user.settings)
            await session.flush()

            await session.commit()
            await engine.dispose()
            return user

    @staticmethod
    async def check_user_exists(VkID: int = None, TgName: str = None):
        async with session_factory() as session:
            query = select(User).where(User.TgName == TgName) if TgName else select(User).where(User.VkID == VkID)
            record_exist = bool((await session.execute(query)).first())
            await engine.dispose()
            return record_exist

    @staticmethod
    async def select_user(VkID: int = None, TgName: str = None) -> User | bool:
        """
        Получаем пользователя из БД. Если его нет возвращаем False
        :param TgName:
        :param VkID:
        :return: Объект User или False, если записи в БД нет
        """
        async with session_factory() as session:
            query = select(User).where(User.VkID == VkID) if VkID else select(User).where(User.TgName == TgName)
            record_exist = bool((await session.execute(query)).first())

            if record_exist:
                if VkID:
                    query = select(User).where(User.VkID == VkID).options(selectinload(User.settings))
                else:
                    query = select(User).where(User.TgName == TgName).options(selectinload(User.settings))

                result = await session.execute(query)
                user = result.scalars().one()

                query = select(Settings).where(Settings.ID == user.ID)
                result = await session.execute(query)
                settings = result.scalars().one()

                user.settings = settings
                await engine.dispose()
                return user

            else:
                return False

    @staticmethod
    async def update_user(user: User):
        async with session_factory() as session:
            user_old = await session.get(User, user.ID)

            for key, value in user.__dict__.items():
                if key not in ('_sa_instance_state', 'settings'):
                    try:
                        setattr(user_old, key, value)
                    except AttributeError:
                        pass

            await session.commit()

            settings_old = await session.get(Settings, user.ID)

            for key, value in user.settings.__dict__.items():
                if key != '_sa_instance_state':
                    try:
                        setattr(settings_old, key, value)
                    except AttributeError:
                        pass

            await session.commit()
            await engine.dispose()

    @staticmethod
    async def merge_records(vk_user: User, tg_name: str):
        async with session_factory() as session:
            query = select(User).where(User.TgName == tg_name)
            result = await session.execute(query)
            tg_user = result.scalars().one()

            tg_user.VkID = vk_user.VkID
            tg_user.VkFirstName = vk_user.VkFirstName
            tg_user.VkLastName = vk_user.VkLastName
            tg_user.first_conn = min(vk_user.first_conn, tg_user.first_conn)
            tg_user.action = vk_user.action
            tg_user.sex = vk_user.sex

            if tg_user.groups and vk_user.groups:
                tg_user.groups = [tg_user.groups[0]] + list(set(tg_user.groups[1:] + vk_user.groups[1:]))
            elif vk_user.groups:
                tg_user.groups = vk_user.groups

            await session.commit()

            query = delete(User).where(User.ID == vk_user.ID)
            await session.execute(query)

            await session.commit()
            await engine.dispose()


class BooksDB:
    @staticmethod
    async def insert_books(books: Books):
        async with session_factory() as session:
            session.add(books)
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def select_books(course: str):
        async with session_factory() as session:
            query = select(Books).where(Books.course == course)
            record_exist = bool((await session.execute(query)).first())

        if record_exist:
            async with session_factory() as session:
                query = select(Books).where(Books.course == course)
                result = await session.execute(query)
                books = result.scalars().one()

        else:
            books = Books(course=course)
            await BooksDB.insert_books(books)

            async with session_factory() as session:
                query = select(Books).where(Books.course == course)
                result = await session.execute(query)
                books = result.scalars().one()

        return books

    @staticmethod
    async def update_books(books: Books):
        async with session_factory() as session:
            query = select(Books).where(Books.course == books.course)
            result = await session.execute(query)
            books_old = result.scalars().one()

            books_old.books = books.books

            await session.commit()
            await engine.dispose()


class HomeworksDB:
    @staticmethod
    async def insert_homeworks(homeworks: Homeworks):
        async with session_factory() as session:
            session.add(homeworks)
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def select_homeworks(group: str):
        async with session_factory() as session:
            query = select(Homeworks).where(Homeworks.group == group)
            record_exist = bool((await session.execute(query)).first())

        if record_exist:
            async with session_factory() as session:
                query = select(Homeworks).where(Homeworks.group == group)
                result = await session.execute(query)
                homeworks = result.scalars().one()

        else:
            homeworks = Homeworks(group=group)
            await HomeworksDB.insert_homeworks(homeworks)

            async with session_factory() as session:
                query = select(Homeworks).where(Homeworks.group == group)
                result = await session.execute(query)
                homeworks = result.scalars().one()

        await engine.dispose()
        return homeworks

    @staticmethod
    async def update_homeworks(homeworks: Homeworks):
        async with session_factory() as session:
            query = select(Homeworks).where(Homeworks.group == homeworks.group)
            result = await session.execute(query)
            homeworks_old = result.scalars().one()

            homeworks_old.homeworks = homeworks.homeworks

            await session.commit()
            await engine.dispose()


class WorkshopsDB:
    @staticmethod
    async def insert_workshops(workshops: Workshops):
        async with session_factory() as session:
            session.add(workshops)
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def select_workshops(course: str):
        async with session_factory() as session:
            query = select(Workshops).where(Workshops.course == course)
            record_exist = bool((await session.execute(query)).first())

        if record_exist:
            async with session_factory() as session:
                query = select(Workshops).where(Workshops.course == course)
                result = await session.execute(query)
                workshops = result.scalars().one()

        else:
            workshops = Workshops(course=course)
            await WorkshopsDB.insert_workshops(workshops)

            async with session_factory() as session:
                query = select(Workshops).where(Workshops.course == course)
                result = await session.execute(query)
                workshops = result.scalars().one()

        return workshops

    @staticmethod
    async def update_workshops(workshops: Workshops):
        async with session_factory() as session:
            query = select(Workshops).where(Workshops.course == workshops.course)
            result = await session.execute(query)
            workshops_old = result.scalars().one()

            workshops_old.workshops = workshops.workshops

            await session.commit()
            await engine.dispose()


class ElectionsDB:
    @staticmethod
    async def create_table_():
        async with engine.begin() as conn:
            await conn.run_sync(ElectionsDB.__table__.create)

    @staticmethod
    async def insert_elections(elections: Elections):
        async with session_factory() as session:
            session.add(elections)
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def select_elections(vk_id: int):
        async with session_factory() as session:
            query = select(Elections).where(Elections.id == vk_id)
            record_exist = bool((await session.execute(query)).first())

        if record_exist:
            async with session_factory() as session:
                query = select(Elections).where(Elections.id == vk_id)
                result = await session.execute(query)
                workshops = result.scalars().one()

        else:
            elections = Elections(vk_id=vk_id)
            await ElectionsDB.insert_elections(elections)

            async with session_factory() as session:
                query = select(Elections).where(Elections.id == vk_id)
                result = await session.execute(query)
                workshops = result.scalars().one()

        return workshops

    @staticmethod
    async def update_elections(elections: Elections):
        async with session_factory() as session:
            elections_old = await session.get(Elections, elections.id)

            for key, value in elections.__dict__.items():
                if key != '_sa_instance_state':
                    try:
                        setattr(elections_old, key, value)
                    except AttributeError:
                        pass

            await session.commit()


async def get_table_size(table_name: str):
    async with engine.begin() as conn:
        result = await conn.execute(text(f"""
                        SELECT pg_size_pretty(pg_total_relation_size('"public"."{table_name}"')) AS size;
                                         """))
        table_size = result.fetchone()[0]
        print(f"Размер таблицы: {table_size}")


if __name__ == '__main__':
    asyncio.run(get_table_size('users'))
