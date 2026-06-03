from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.Database.Database import Base, ipk, uid, cid, str20, str50, str255


class Banned(Base):
    __tablename__ = 'banned'
    id: Mapped[ipk]

    chat_id:    Mapped[cid]
    admin_id:   Mapped[uid]
    user_id:    Mapped[uid]
    reason:     Mapped[str50|None]

    __table_args__ = (
        CheckConstraint('admin_id != user_id'),
    )

class Chats(Base):
    __tablename__ = 'chats'
    id: Mapped[ipk]

    chat_id:    Mapped[int]
    title:      Mapped[str50]

    welcome_text: Mapped[str255] = mapped_column(default=False)

    enable_random_cat:  Mapped[bool] = mapped_column(default=False)
    is_vip:             Mapped[bool] = mapped_column(default=False)
    new_version:        Mapped[bool|None]

class UsersInChats(Base):
    __tablename__ = 'users_in_chats'
    id: Mapped[ipk]

    chat_id:    Mapped[cid]
    user_id:    Mapped[uid]
    is_admin:   Mapped[bool] = mapped_column(default=False)
    is_owner:   Mapped[bool] = mapped_column(default=False)

    warn: Mapped[int] = mapped_column(default=0)

class WarnWordsChats(Base):
    __tablename__ = 'warn_words_chats'
    id: Mapped[ipk]

    chat_id: Mapped[cid]
    word: Mapped[str20]