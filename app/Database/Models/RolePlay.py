from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.Database.Database import Base, ipk, uid


class RelationShip(Base):
    __tablename__ = 'relation_ship'
    id: Mapped[ipk]

    user_id: Mapped[uid]
    target_id: Mapped[uid]
    score: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        CheckConstraint('user_id != target_id'),
    )