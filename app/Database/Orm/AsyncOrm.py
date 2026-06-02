from sqlalchemy import select

from app.Database.Models.Administration import Chats, UsersInChats
from app.Database.Database import Base, async_session_factory, async_engine
from app.Database.Models.General import Users


class AsyncORM:
    @staticmethod
    async def recreate_tables():
        async with async_engine.connect() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()

    @staticmethod
    async def add_user_to_chat(user_id, name, chat_id, title):
        async with async_session_factory() as session:
            chat = await session.execute(
                select(Chats).where(Chats.chat_id==chat_id)
            ).scalars().first()
            if not chat:
                chat = Chats(chat_id=chat_id, title=title)
                session.add(chat)
                session.flush()

            user = await session.execute(
                select(Users).where(Users.user_id==user_id)
            ).scalars().first()
            if not user:
                user = Users(user_id=user_id, name=name)
                session.add(user)
                session.flush()

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
