import random

from sqlalchemy import select, or_, delete

from Database.Models.General import CatsImages, Commands
from app.Database.Models.Administration import Chats, UsersInChats
from app.Database.Database import Base, async_session_factory, async_engine
from app.Database.Models.General import Users


class AsyncORM:
    ALLOWED_METHODS = ['add_user', 'add_chat', 'send_random_cat']

    @classmethod
    async def do_func(cls, func_str, *args):
        if func_str in cls.ALLOWED_METHODS:
            func = globals().get(func_str)
            if func:
                return await func(*args)
            else:
                return "Функция еще не реализована"
        return None

    @classmethod
    async def recreate_tables(cls):
        async with async_engine.connect() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()

    @classmethod
    async def add_user_to_chat(cls, user_id, name, chat_id, title):
        async with async_session_factory() as session:
            await cls.add_chat(chat_id, title)
            await cls.add_user(user_id, name)

            uic = await session.execute(
                select(UsersInChats).where(
                    UsersInChats.user_id==user_id,
                    UsersInChats.chat_id==chat_id
                )
            ).scalars().first()
            if not uic:
                uic = UsersInChats(chat_id=chat_id, user_id=user_id)
                session.add(uic)

            session.commit()

    @classmethod
    async def add_user(cls, user_id, name):
        async with async_session_factory() as session:
            user = await session.execute(
                select(Users).where(Users.user_id==user_id)
            ).scalars().first()

            if not user:
                user = Users(user_id=user_id, name=name)
                session.add(user)
                session.flush()

            session.commit()

    @classmethod
    async def add_chat(cls, chat_id, title):
        async with async_session_factory() as session:
            chat = await session.execute(
                select(Chats).where(Chats.chat_id==chat_id)
            ).scalars().first()

            if not chat:
                chat = Chats(chat_id=chat_id, title=title)
                session.add(chat)
                session.flush()

            session.commit()

    @classmethod
    async def send_random_cat(cls):
        try:
            async with async_session_factory() as session:
                cats_list:list[tuple] = await session.execute(select(CatsImages)).scalars().all()
                return cats_list[random.randint(0, len(cats_list)-1)].__dict__.copy().pop('_sa_instance_state', None)
        except ValueError:
            return None
        except Exception as e:
            print(e)
            return None

    @classmethod
    async def send_response(cls, trigger_str, user_id:int = None, chat_id:int = None, *args) -> None|tuple:
        try:
            async with async_session_factory() as session:
                query = (
                    select(Commands)
                    .where(
                        Commands.trigger == trigger_str,
                        or_(Commands.user_id == user_id, Commands.user_id.is_(None)),
                        or_(Commands.chat_id == chat_id, Commands.chat_id.is_(None))
                    )
                    # Сортируем, пользовательские команды более приоритетнее публичных
                    .order_by(Commands.user_id.desc(), Commands.chat_id.desc())
                )
                command: Commands = await session.execute(query).scalars().first()

                if not command:
                    return None

                response = command.response

                func_res = await cls.do_func(command.function, *args) if command.function else None

                return response, func_res

        except Exception as e:
            print(e)
            return None


    @classmethod
    async def delete_command(cls, trigger_str, user_id:int = None, chat_id:int = None):
        try:
            async with async_session_factory() as session:
                query = (
                    delete(Commands)
                    .where(
                        Commands.trigger == trigger_str,
                        Commands.user_id == user_id,
                        Commands.chat_id == chat_id,
                    )
                )
                await session.execute(query)
                await session.commit()
                return True

        except Exception as e:
            print(f"\033[34m{e}\033[0m")
            return False