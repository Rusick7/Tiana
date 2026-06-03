from datetime import datetime
from typing import Annotated

from sqlalchemy import String, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.Database.Settings import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,
)

async_session_factory = async_sessionmaker(async_engine)


str1 = Annotated[str, 1]
str20 = Annotated[str, 20]
str50 = Annotated[str, 50]
str255 = Annotated[str, 255]
ipk = Annotated[int, mapped_column(primary_key=True)]
uid = Annotated[int, mapped_column(ForeignKey('users.user_id'))]
cid = Annotated[int, mapped_column(ForeignKey('chats.chat_id'))]

class Base(DeclarativeBase):
    type_annotation_map = {
        str1: String(1),
        str20: String(20),
        str50: String(50),
        str255: String(255),
    }

    description: Mapped[str255]
    notes: Mapped[str255]

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(),
        onupdate=datetime.utcnow
    )