import traceback
from typing import Sequence, List

from sqlalchemy import select, delete, text, insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload
from vkbottle.bot import Message

from Config.Config import global_settings, bot
from Scripts.Others import get_sex_of_person_by_name
from Server.Models import Base, User, Settings, Books, Homeworks, Workshops, Elections, Votes, Exam, QuizUser, Quiz, \
    CustomLesson, WeekType, GroupName, Lesson

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
            vk_info = await message.get_user()
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

    @staticmethod
    async def get_all_users():
        async with session_factory() as session:
            users = await session.execute(select(User))
            return users.scalars().all()


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
    async def create_table():
        async with engine.begin() as conn:
            await conn.run_sync(Elections.__table__.create)

    @staticmethod
    async def insert(election: Elections):
        async with session_factory() as session:
            session.add(election)
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def select(vk_id: int) -> Elections:
        async with session_factory() as session:
            query = select(Elections).where(Elections.vk_id == vk_id)
            record_exist = bool((await session.execute(query)).first())

        if record_exist:
            async with session_factory() as session:
                query = select(Elections).where(Elections.vk_id == vk_id)
                result = await session.execute(query)
                election = result.scalars().one()

        # else:
        #     election = Elections(vk_id=vk_id)
        #     await ElectionsDB.insert(election)
        #
        #     async with session_factory() as session:
        #         query = select(Elections).where(Elections.vk_id == vk_id)
        #         result = await session.execute(query)
        #         election = result.scalars().one()

        await engine.dispose()
        return election

    @staticmethod
    async def update(election: Elections):
        async with session_factory() as session:
            query = select(Elections).where(Elections.id == election.id)
            result = await session.execute(query)
            election_old = result.scalars().one()

            for key, value in election.__dict__.items():
                if key not in ('_sa_instance_state'):
                    try:
                        setattr(election_old, key, value)
                    except AttributeError:
                        pass

            await session.commit()
            await engine.dispose()

    @staticmethod
    async def get_all_choices() -> List[Elections]:
        async with session_factory() as session:
            result = await session.execute(select(Elections).order_by(Elections.id))
            elections = result.scalars().all()
            await engine.dispose()

        return elections

    @staticmethod
    async def delete_user(election: Elections):
        async with session_factory() as session:
            await session.execute(delete(Elections).where(Elections.id == election.id))
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def insert_vote(vote: Votes):
        async with session_factory() as session:
            session.add(vote)
            await session.commit()
            await engine.dispose()


async def get_table_size(table_name: str):
    async with engine.begin() as conn:
        result = await conn.execute(text(f"""
                        SELECT pg_size_pretty(pg_total_relation_size('"public"."{table_name}"')) AS size;
                                         """))
        table_size = result.fetchone()[0]
        print(f"Размер таблицы: {table_size}")


class SessionDB:
    @staticmethod
    async def insert(exam: Exam):
        async with session_factory() as session:
            session.add(exam)
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def select(group: str):
        async with session_factory() as session:
            query = select(Exam).filter(Exam.group == group).order_by(Exam.exam_datetime)
            result = await session.execute(query)
            exams = result.scalars().all()
            await engine.dispose()
            return exams

    @staticmethod
    async def update(exam: Exam):
        async with session_factory() as session:
            query = select(Exam).filter(Exam.group == exam.group, Exam.name == exam.name)
            result = await session.execute(query)
            exam_old = result.scalars().one()

            exam_old.teacher = exam.teacher
            exam_old.exam_datetime = exam.exam_datetime
            exam_old.room = exam.room

            await session.commit()
            await engine.dispose()


class QuizDB:
    @staticmethod
    async def create_table():
        async with engine.begin() as conn:
            await conn.run_sync(Quiz.__table__.create)

    @staticmethod
    async def insert(question: Quiz):
        async with session_factory() as session:
            session.add(question)
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def select(num: int) -> Quiz:
        async with session_factory() as session:
            query = select(Quiz).where(Quiz.id == num)
            result = await session.execute(query)
            question = result.scalars().one()
            await engine.dispose()
            return question

    @staticmethod
    async def update(question: Quiz):
        async with session_factory() as session:
            query = select(Quiz).where(Quiz.id == question.id)
            result = await session.execute(query)
            question_old = result.scalars().one()

            question_old.question = question.question
            question_old.variants = question.variants
            question_old.answer = question.answer
            question_old.desc = question.desc

            await session.commit()
            await engine.dispose()


class QuizUserDB:
    @staticmethod
    async def create_table():
        async with engine.begin() as conn:
            await conn.run_sync(QuizUser.__table__.create)

    @staticmethod
    async def insert(quiz_user: QuizUser):
        async with session_factory() as session:
            session.add(quiz_user)
            await session.commit()
            await engine.dispose()

    @staticmethod
    async def select(user_id: int) -> QuizUser:
        async with session_factory() as session:
            query = select(QuizUser).where(QuizUser.user_id == user_id)
            result = await session.execute(query)
            quiz_user = result.scalars().one_or_none()
            await engine.dispose()
            return quiz_user

    @staticmethod
    async def update(quiz_user: QuizUser):
        async with session_factory() as session:
            query = select(QuizUser).where(QuizUser.id == quiz_user.id)
            result = await session.execute(query)
            quiz_user_old = result.scalars().one()

            quiz_user_old.count_true_answers = quiz_user.count_true_answers

            if quiz_user.end_datetime:
                quiz_user_old.end_datetime = quiz_user.end_datetime

            await session.commit()
            await engine.dispose()


class GroupNameDB:
    @staticmethod
    async def create_table():
        async with engine.begin() as conn:
            await conn.run_sync(GroupName.__table__.create)

    @staticmethod
    async def insert(group: GroupName = None, groups: list[GroupName] = None):
        async with session_factory() as session:
            session.add_all(groups) if groups else session.add(group)
            await session.commit()

    @staticmethod
    async def select(group_name: str) -> GroupName:
        async with session_factory() as session:
            query = select(GroupName).where(GroupName.group_name == group_name)
            result = await session.execute(query)
            group = result.scalars().one_or_none()

            return group


class LessonScheduleDB:
    @staticmethod
    async def create_table():
        async with engine.begin() as conn:
            await conn.run_sync(Lesson.__table__.create)

    @staticmethod
    async def update_or_insert_list_lessons(lessons: list[tuple[Lesson, str]] = None):
        async with (session_factory() as session):
            groups = (await session.execute(select(GroupName))).scalars().all()

            db_groups_names = set([g.group_name for g in groups])
            schedule_groups_names = set(x[1] for x in lessons)

            if len(schedule_groups_names - db_groups_names) > 0:
                expected_groups = list(schedule_groups_names - db_groups_names)
                await GroupNameDB.insert(groups=[GroupName(group_name=g) for g in expected_groups])
                groups = (await session.execute(select(GroupName))).scalars().all()

            groups = {g.group_name: g.id for g in groups}

            try:
                lessons_data = [lesson.get_dict_values(group_id=groups[group_name]) for lesson, group_name in lessons]

                query = insert(Lesson).values(lessons_data)
                query = query.on_conflict_do_update(constraint='uq_schedule_unique_lesson',
                                                    set_={
                                                        "lesson": query.excluded.lesson,
                                                        "teacher": query.excluded.teacher,
                                                        "room": query.excluded.room
                                                    })
                await session.execute(query)
                await session.commit()

            except KeyError:
                traceback.print_exc()
                await session.close()

    @staticmethod
    async def update_or_insert_one_lesson(lesson: Lesson, group_name: str):
        async with (session_factory() as session):
            group = (await session.execute(
                select(GroupName).where(GroupName.group_name == group_name))).scalars().one_or_none()

            if group:
                lesson_data = lesson.get_dict_values(group_id=group.id)
                query = insert(Lesson).values(lesson_data)
                query = query.on_conflict_do_update(constraint='uq_schedule_unique_lesson',
                                                    set_={
                                                        "lesson": query.excluded.lesson,
                                                        "teacher": query.excluded.teacher,
                                                        "room": query.excluded.room
                                                    })
                await session.execute(query)
                await session.commit()

            else:
                await session.close()

    @staticmethod
    async def select(group_name: str, weekday: int, week_type: WeekType = None) -> list[Lesson] | None:
        async with (session_factory() as session):
            group = await GroupNameDB.select(group_name=group_name)
            if group:
                query = select(Lesson).where(Lesson.group_id == group.id, Lesson.weekday == weekday
                                             ).order_by(Lesson.lesson_number, Lesson.week_type)
                if week_type:
                    query = select(Lesson).where(Lesson.group_id == group.id, Lesson.weekday == weekday,
                                                 Lesson.week_type == week_type,
                                                 ).order_by(Lesson.lesson_number, Lesson.week_type)
                else:
                    query = select(Lesson).where(Lesson.group_id == group.id, Lesson.weekday == weekday
                                                 ).order_by(Lesson.lesson_number, Lesson.week_type)

                result = await session.execute(query)
                lessons = result.scalars().all()
                return lessons[0] if type(lessons) is tuple else lessons

    @staticmethod
    async def select_one_lesson(group_name: str, weekday: int, lesson_number: int, week_type: WeekType = None) -> Lesson:
        async with session_factory() as session:
            group = await GroupNameDB.select(group_name=group_name)

            query = select(Lesson).where(Lesson.group_id == group.id,
                                         Lesson.weekday == weekday,
                                         Lesson.lesson_number == lesson_number,
                                         Lesson.week_type == week_type)

            result = await session.execute(query)
            lesson = result.scalars().one_or_none()

            return lesson


class CustomLessonScheduleDB:
    @staticmethod
    async def create_table():
        async with engine.begin() as conn:
            await conn.run_sync(CustomLesson.__table__.create)

    @staticmethod
    async def update_or_insert_one_lesson(lesson: CustomLesson, group_name: str):
        async with (session_factory() as session):
            group = (await session.execute(
                select(GroupName).where(GroupName.group_name == group_name))).scalars().one_or_none()

            if group:
                lesson_data = lesson.get_dict_values(group_id=group.id)
                query = insert(CustomLesson).values(lesson_data)
                query = query.on_conflict_do_update(constraint='uq_custom_schedule_unique_lesson',
                                                    set_={
                                                        "lesson": query.excluded.lesson,
                                                        "teacher": query.excluded.teacher,
                                                        "room": query.excluded.room
                                                    })
                await session.execute(query)
                await session.commit()

            else:
                await session.close()

    @staticmethod
    async def select(group_name: str, weekday: int, week_type: WeekType) -> list[CustomLesson] | None:
        async with session_factory() as session:
            group = await GroupNameDB.select(group_name=group_name)
            if group:
                query = select(CustomLesson).where(CustomLesson.group_id == group.id,
                                                   CustomLesson.weekday == weekday)
                if week_type:
                    query.where(CustomLesson.week_type == week_type)

                query.order_by(CustomLesson.week_type, CustomLesson.lesson_number)

                result = await session.execute(query)
                lessons = result.scalars().all()

                return lessons[0] if type(lessons) is tuple else lessons

            else:
                await session.close()

    @staticmethod
    async def select_one_lesson(group_name: str, weekday: int, lesson_number: int,
                                week_type: WeekType = None) -> List[CustomLesson]:
        async with session_factory() as session:
            group = await GroupNameDB.select(group_name=group_name)
            query = select(CustomLesson).where(CustomLesson.group_id == group.id,
                                               CustomLesson.weekday == weekday,
                                               CustomLesson.lesson_number == lesson_number,
                                               CustomLesson.week_type == week_type)

            result = await session.execute(query)
            lessons = result.scalars().one_or_none()

            return lessons
