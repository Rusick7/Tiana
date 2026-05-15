from enum import Enum

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.Database.Database import Base, str50, ipk, uid


class Genders(Enum):
    M = 'Male'
    F = 'Female'

class Users(Base):
    __tablename__ = 'users'

    id: Mapped[ipk]
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str50]
    gender: Mapped[Genders|None]
    new_version: Mapped[bool] = mapped_column(default=False)

class Commands(Base):
    __tablename__ = 'commands'

    id: Mapped[ipk]
    user_id: Mapped[uid|None] # Null for public commands
    trigger: Mapped[str50]
    response: Mapped[str50]

    # 'relation_ship.score + 10' добавляет в таблицу там где score число 10
    # 'banned + target' в список забаненных добавляет тг user_id (target)
    effect: Mapped[str50]
