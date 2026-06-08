import html
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, or_, delete, func
from sqlalchemy.sql.functions import user

from app.Database.Models.General import CatsImages, Commands
from app.Database.Models.Administration import Chats, UsersInChats, UsersStatsInChats
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
    async def recreate_tables(cls) -> None:
        async with async_engine.connect() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()



    # ADD TO DATABASE

    @classmethod
    async def add_user_to_chat(cls, user_id, name, chat_id, title) -> bool:
        try:
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

                await session.commit()
            return True
        except Exception as e:
            print(f"\033[34m{e}\033[0m")
            return False

    @classmethod
    async def add_user(cls, user_id, name) -> bool:
        try:
            async with async_session_factory() as session:
                user = await session.execute(
                    select(Users).where(Users.user_id==user_id)
                ).scalars().first()

                if not user:
                    user = Users(user_id=user_id, name=name)
                    session.add(user)
                    session.flush()

                await session.commit()
            return True
        except Exception as e:
            print(f"\033[34m{e}\033[0m")
            return False

    @classmethod
    async def add_chat(cls, chat_id, title) -> bool:
        try:
            async with async_session_factory() as session:
                chat = await session.execute(
                    select(Chats).where(Chats.chat_id==chat_id)
                ).scalars().first()

                if not chat:
                    chat = Chats(chat_id=chat_id, title=title)
                    session.add(chat)
                    session.flush()

                await session.commit()
            return True
        except Exception as e:
            print(f"\033[34m{e}\033[0m")
            return False

    # Сохранение нового сообщения
    @classmethod
    async def save_message(cls, chat_id: int, user_id: int, message: str = None) -> bool:
        try:
            async with async_session_factory() as session:
                new_msg = UsersStatsInChats(chat_id=chat_id, user_id=user_id, message=message)
                session.add(new_msg)
                await session.commit()
            return True
        except Exception as e:
            print(f"\033[34m{e}\033[0m")
            return False



    # GET FROM DATABASE

    @classmethod
    async def get_random_cat(cls) -> dict|None: # func()['image'] - image
        try:
            async with async_session_factory() as session:
                cats_list:list[tuple] = (await session.execute(select(CatsImages))).scalars().all()
                return cats_list[random.randint(0, len(cats_list)-1)].__dict__.copy().pop('_sa_instance_state', None)

        except Exception as e:
            print(f"\033[34m{e}\033[0m")

    @classmethod
    async def get_user(cls, user_id, username) -> Users|None:
        try:
            async with async_session_factory() as session:
                return (await session.execute(select(Users).where(or_(Users.user_id==user_id, Users.username==username)))).scalar_one_or_none()
        except Exception as e:
            print(f"\033[34m{e}\033[0m")






    # Подсчет сообщений за определенный период
    @classmethod
    async def get_messages_count(cls, chat_id: int, period: str, user_id: int = None) -> int:
        now = datetime.now(timezone.utc)

        periods_map = {'d': {'days': 1}, 'w': {'days': 7}, 'm': {'days': 30}, 'y': {'days': 365}}

        delta_args = periods_map.get(period)
        start_date = now - timedelta(**delta_args) if delta_args else None

        async with async_session_factory() as session:
            query = select(func.count(UsersStatsInChats.id)).where(UsersStatsInChats.chat_id == chat_id)
            if user_id:
                # noinspection PyTypeChecker
                query = query.where(UsersStatsInChats.user_id == user_id)

            # Добавляем фильтр по дате, если выбран конкретный период
            if start_date:
                query = query.where(UsersStatsInChats.created_at >= start_date)

            result = await session.execute(query)
            return result.scalar() or 0



    @classmethod
    async def get_response(cls, trigger_str, chat_id:int = None,
                            user_id:int = None,         username:str = None,
                            target_user_id:int = None,  target_username:str = None,
                            *args) -> None|tuple:
        trigger_str=trigger_str.lower()

        async def replace_new_text(_user: Users|None, _username)->str:
            if _user:
                return f'<a href="tg://user?id={user.user_id}">{html.escape(str(_user.name))}</a>'
            else:
                return f'<a href="https://t.me/{_username}">{html.escape(_username)}</a>'

        try:
            async with async_session_factory() as session:
                _user = await cls.get_user(user_id=user_id, username=username)
                _target = await cls.get_user(user_id=target_user_id, username=target_username)

                query = (
                    select(Commands)
                    .where(
                        Commands.trigger == trigger_str,
                        or_(Commands.user_id == user_id, Commands.user_id.is_(None)),
                        or_(Commands.chat_id == chat_id, Commands.chat_id.is_(None)) # Если ид чата равен ид чату или она пуста
                    )
                    # Сортируем, пользовательские команды более приоритетнее публичных
                    .order_by(Commands.user_id.desc(), Commands.chat_id.desc())
                )
                command: Commands = (await session.execute(query)).scalars().first()

                if command:
                    response = command.response

                    # добавление эмодзи
                    if command.mark or (_user and not _user.new_version):
                        response = command.mark + ' | ' + response

                    # создание ссылки
                    if '%u' in response:
                        response = response.replace('%u', await replace_new_text(_user, username))
                    if '%t' in response:
                        response = response.replace('%t', await replace_new_text(_target, target_username))

                    func_res = await cls.do_func(command.function, *args) if command.function else None

            return response, func_res

        except Exception as e:
            print(f"\033[34m{e}\033[0m")



    # DELETE FROM DATABASE

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