from enum import Enum

from sqlalchemy import BigInteger, ForeignKey, String, CheckConstraint, LargeBinary, not_, and_
from sqlalchemy.orm import Mapped, mapped_column

from app.Database.Database import Base, str50, ipk, uid, cid


class Genders(Enum):
    M = 'Male'
    F = 'Female'
    Fb = 'Femboy'

class Users(Base):
    __tablename__ = 'users'
    id: Mapped[ipk]

    user_id:    Mapped[int] = mapped_column(BigInteger, unique=True)
    name:       Mapped[str50]
    gender:     Mapped[Genders|None]
    is_vip:         Mapped[bool] = mapped_column(default=False)
    new_version:    Mapped[bool] = mapped_column(default=False)

class Commands(Base):
    __tablename__ = 'commands'
    id: Mapped[ipk]

    user_id:    Mapped[uid|None] # Null for public commands
    chat_id:    Mapped[cid|None] # Null for public commands
    trigger:    Mapped[str50]
    response:   Mapped[str50]

    __table_args__ = (
        CheckConstraint(and_())
        # ('(user_id IS     NULL AND chat_id IS NOT NULL) OR '
        #                 '(user_id IS NOT NULL AND chat_id IS     NULL)'),
    )

class CatsImages(Base):
    __tablename__ = 'cats_images'
    id: Mapped[ipk]

    name:   Mapped[str50|None]
    text:   Mapped[str50|None]
    image:  Mapped[bytes] = mapped_column(LargeBinary)

    gender: Mapped[Genders|None]
    count:  Mapped[int] = mapped_column(default=0)

    is_funny:       Mapped[bool|None] = mapped_column(default=None)
    is_sad:         Mapped[bool|None] = mapped_column(default=None)
    is_angry:       Mapped[bool|None] = mapped_column(default=None)
    is_sleeping:    Mapped[bool|None] = mapped_column(default=None)

    is_kitten:      Mapped[bool|None] = mapped_column(default=None)
    has_clothes:    Mapped[bool|None] = mapped_column(default=None)

    is_real_life:   Mapped[bool|None] = mapped_column(default=None)
    is_anime:       Mapped[bool|None] = mapped_column(default=None)

    __table_args__ = (
        CheckConstraint(not_(is_real_life == is_anime)),
    )

class Effects(Base):
    __tablename__ = 'effects'
    id: Mapped[ipk]

    user_id:    Mapped[uid|None]
    command_id: Mapped[int] = mapped_column(ForeignKey('commands.id'))
    table:      Mapped[str50]
    column:     Mapped[str50|None]
    action:     Mapped[str] = mapped_column(String(1))

    paste_admin_id:     Mapped[bool] = mapped_column(default=False)
    paste_user_id:      Mapped[bool] = mapped_column(default=False)
    paste_target_id:    Mapped[bool] = mapped_column(default=False)
    paste_chat_id:      Mapped[bool] = mapped_column(default=False)
    paste_value:        Mapped[bool] = mapped_column(default=False)
    paste_description:  Mapped[bool] = mapped_column(default=False)