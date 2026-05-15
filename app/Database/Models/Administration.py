from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.Database.Database import Base, ipk, uid, str50, cid


class Banned(Base):
    __tablename__ = 'banned'

    id: Mapped[ipk]
    chat_id: Mapped[cid]
    admin_id: Mapped[uid]
    user_id: Mapped[uid]
    reason: Mapped[str50|None]

    __table_args__ = (
        CheckConstraint('admin_id != user_id'),
    )

class Chats(Base):
    __tablename__ = 'chats'

    id: Mapped[ipk]
    chat_id: Mapped[int]
    title: Mapped[str50]

class UsersInChats(Base):
    __tablename__ = 'users_in_chats'

    id: Mapped[ipk]
    chat_id: Mapped[cid]
    user_id: Mapped[uid]
    is_admin: Mapped[bool] = mapped_column(default=False)