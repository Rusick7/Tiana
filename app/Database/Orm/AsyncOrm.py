import html
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, or_, delete, func

from app.Database.Models.General import CatsImages, Commands
from app.Database.Models.Administration import Chats, UsersInChats, UsersStatsInChats
from app.Database.Database import Base, async_session_factory, async_engine
from app.Database.Models.General import Users


class AsyncORM:
    ALLOWED_METHODS = ['add_user', 'add_chat', 'get_random_cat', 'get_random_cat_image']

    @classmethod
    async def do_func(cls, func_str, *args):
        if func_str in cls.ALLOWED_METHODS:
            func_ = getattr(cls, func_str, None)
            if func_:
                return await func_(*args)
            print("Функция еще не реализована")
        return None

    @classmethod
    async def recreate_tables(cls) -> None:
        async with async_engine.connect() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()



    # =================================================
    # ADD TO DATABASE
    # =================================================
    @classmethod
    async def add_logic(cls, query, new_obj, session) -> bool:
        try:
            db_values = (await session.execute(query)).scalar_one_or_none()

            if not db_values:
                session.add(new_obj)
                return True

            return False

        except Exception as e:
            print(f"\033[34m {e} \033[0m")
            return False

    @classmethod
    async def add_user(cls, user_id, username, name, session = None) -> bool:
        # init переменные
        user_query = select(Users).where(Users.user_id == user_id)
        user_new = Users(user_id=user_id, username=username, name=name)

        # Если есть сессия используем её иначе создаем новую
        session = session if session is not None else async_session_factory()

        try:
            if not session:
                async with async_session_factory() as session:
                    is_added = await cls.add_logic(query=user_query, new_obj=user_new, session = session)
                    if is_added:
                        await session.commit()
                        return True

            elif session:
                is_added = await cls.add_logic(query=user_query, new_obj=user_new, session = session)
                if is_added:
                    await session.commit()
                    return True

            print(f"\033[34m Failed to add user. Details: user_id={user_id} \033[0m")
            return False

        except Exception as e:
            print(f"\033[34m {e} \033[0m")
            return False

    @classmethod
    async def add_chat(cls, chat_id, title, session = None) -> bool:
        # init переменные
        chat_query = select(Chats).where(Chats.chat_id==chat_id)
        chat_new = Chats(chat_id=chat_id, title=title)

        try:
            if not session:
                async with async_session_factory() as session:
                    is_added = await cls.add_logic(query=chat_query, new_obj=chat_new, session = session)
                    if is_added:
                        await session.commit()
                        return True

            elif session:
                is_added = await cls.add_logic(query=chat_query, new_obj=chat_new, session = session)
                if is_added:
                    await session.commit()
                    return True

            print(f"\033[34m Failed to add chat. Details: chat_id={chat_id} \033[0m")
            return False

        except Exception as e:
            print(f"\033[34m {e} \033[0m")
            return False

    @classmethod
    async def add_user_to_chat(cls, user_id, username, name, chat_id, title) -> bool:
        # init переменные
        uic_query = select(UsersInChats).where(
            UsersInChats.user_id == user_id,
            UsersInChats.chat_id == chat_id
        )
        uic_new = UsersInChats(chat_id=chat_id, user_id=user_id)

        try:
            async with async_session_factory() as session:
                await cls.add_chat(chat_id=chat_id, title=title, session=session)
                await cls.add_user(user_id=user_id, username=username, name=name, session=session)
                uic_added = await cls.add_logic(uic_query, uic_new, session)

                if uic_added:
                    await session.commit()
                    return True

                await session.rollback()
                return False

        except Exception as e:
            print(f"\033[34m add_user_to_chat: {e} \033[0m")
            return False

    # Сохранение нового сообщения
    @classmethod
    async def save_message(cls, chat_id: int, user_id: int, message: str|None = None) -> bool:
        try:
            async with async_session_factory() as session:
                new_msg = UsersStatsInChats(chat_id=chat_id, user_id=user_id, message=message)
                session.add(new_msg)
                await session.commit()
            return True

        except Exception as e:
            print(f"\033[34m {e} \033[0m")
            return False

    @classmethod
    async def add_command(cls, trigger: str, response: str, mark: str|None,
                          user_id: int|None = None, chat_id: int|None = None,
                          function_str: str|None = None) -> bool:
        try:
            async with async_session_factory() as session:
                new_command = Commands(user_id=user_id, chat_id=chat_id,
                                       trigger=trigger, response=response,
                                       mark=mark, function=function_str)
                session.add(new_command)
                await session.commit()
            return True

        except Exception as e:
            print(f"\033[34m {e} \033[0m")
            return False



    # =================================================
    # GET FROM DATABASE
    # =================================================
    @classmethod
    async def get_random_cat(cls) -> CatsImages|None:
        try:
            async with async_session_factory() as session:
                cats_list:list[CatsImages] = (await session.execute(select(CatsImages))).scalars().all()
                return cats_list[random.randint(0, len(cats_list)-1)]

        except Exception as e:
            print(f"\033[34m {e} \033[0m")

    @classmethod
    async def get_random_cat_image(cls):
        rand_cat = await cls.get_random_cat()
        return rand_cat.image if rand_cat else None

    @classmethod
    async def get_user(cls, user_id: int|None, username: str|None) -> Users|None:
        try:
            async with async_session_factory() as session:
                if user_id:
                    # noinspection PyTypeChecker
                    query = select(Users).where(Users.user_id == user_id)
                elif username:
                    # noinspection PyTypeChecker
                    query = select(Users).where(Users.username == username)
                else:
                    return None
                return (await session.execute(query)).scalar_one_or_none()

        except Exception as e:
            print(f"\033[34m {e} \033[0m")

    # Подсчет сообщений за определенный период
    @classmethod
    async def get_messages_count(cls, chat_id: int, period: str, user_id: int|None = None) -> int:
        # init переменные
        now = datetime.now(timezone.utc) # сегодня

        periods_map = {'d': {'days': 1}, 'w': {'days': 7}, 'm': {'days': 30}, 'y': {'days': 365}}

        delta_args = periods_map.get(period) # разница/период если есть иначе None (ничего)
        start_date = now - timedelta(**delta_args) if delta_args else None # дата отсчета / начальная дата

        async with async_session_factory() as session:
            # создание запроса
            query = select(func.count(UsersStatsInChats.id)).where(UsersStatsInChats.chat_id == chat_id)

            # если есть ид юзера или начальная дата добавлять проверку в запрос
            # noinspection PyTypeChecker
            query = query.where(UsersStatsInChats.user_id == user_id) if user_id else query
            query = query.where(UsersStatsInChats.created_at >= start_date) if start_date else query

            # возвращаем количество сообщений
            return (await session.execute(query)).scalar() or 0



    @classmethod
    async def get_response(cls, trigger_str:str, chat_id:int,
                            user_id:int|None = None,         username:str|None = None,
                            target_user_id:int|None = None,  target_username:str|None = None,
                            *args) -> None|tuple:
        # нормализуем входную строку
        trigger_str=trigger_str.split(' ')[0].lower()

        # функция вставки ссылки только для этого метода
        async def replace_response(user_: Users|None, _username: str)->str:
            if user_:
                return f'<a href="tg://user?id={user_.user_id}">{html.escape(str(user_.name))}</a>'
            else:
                return f'<a href="https://t.me/{_username}">{html.escape(_username)}</a>'

        try:
            async with async_session_factory() as session:
                # init переменные
                _user = await cls.get_user(user_id=user_id, username=username)
                _target = await cls.get_user(user_id=target_user_id, username=target_username)

                # создание запроса
                query = (
                    select(Commands)
                    .where(
                        Commands.trigger == trigger_str,
                        or_(Commands.user_id == user_id, Commands.user_id.is_(None)), # убираем все лишние записи
                        or_(Commands.chat_id == chat_id, Commands.chat_id.is_(None)), # убираем все лишние записи
                    )
                    # Сортируем, пользовательские команды более приоритетнее публичных
                    .order_by(Commands.user_id.desc(), Commands.chat_id.desc())
                )
                # выполнение запроса
                command: Commands = (await session.execute(query)).scalars().first()

                # проверка на запись
                if command:
                    # init переменные
                    response = command.response

                    # добавление эмодзи если есть и вкл новая версия
                    response = command.mark + ' | ' + response if command.mark and _user and not _user.new_version else response

                    # создание ссылки
                    response = response.replace('%u', await replace_response(_user, username)) if '%u' in response else response
                    response = response.replace('%t', await replace_response(_target, target_username)) if '%t' in response else response

                    # выполнение функции если есть
                    func_res = await cls.do_func(command.function, *args) if command.function else None

            return response, func_res

        # \033[34m делает след текст голубым, а \033[0m белым
        except Exception as e:
            print(f"\033[34m {e} \033[0m")



    # =================================================
    # DELETE FROM DATABASE
    # =================================================
    @classmethod
    async def delete_command(cls, trigger_str, user_id:int|None = None, chat_id:int|None = None):
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