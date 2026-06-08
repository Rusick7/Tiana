from enum import Enum

from sqlalchemy import BigInteger, CheckConstraint, LargeBinary, not_, String
from sqlalchemy.orm import Mapped, mapped_column

from app.Database.Database import Base, str20, str50, ipk, uid, cid


class Genders(Enum):
    M = 'Male'
    F = 'Female'
    Fb = 'Femboy'

class Users(Base):
    __tablename__ = 'users'
    id: Mapped[ipk]

    user_id:    Mapped[int] = mapped_column(BigInteger, unique=True)
    username:   Mapped[str50] = mapped_column(BigInteger, unique=True)
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
    mark:       Mapped[str|None] = mapped_column(String(1))

    function: Mapped[str20|None]

class CatsImages(Base):
    __tablename__ = 'cats_images'
    id: Mapped[ipk]

    name:   Mapped[str50|None]
    text:   Mapped[str50|None]
    image:  Mapped[bytes] = mapped_column(LargeBinary)

    gender: Mapped[Genders|None]
    count:  Mapped[int] = mapped_column(default=1)

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