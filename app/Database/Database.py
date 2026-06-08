from datetime import datetime, timezone
from typing import Annotated

from sqlalchemy import String, ForeignKey, DateTime, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.Database.Settings import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,
)

async_session_factory = async_sessionmaker(async_engine)


str20 = Annotated[str, 20]
str50 = Annotated[str, 50]
str255 = Annotated[str, 255]
ipk = Annotated[int, mapped_column(primary_key=True)]
uid = Annotated[int, mapped_column(BigInteger)]
cid = Annotated[int, mapped_column(unique=True)]

class Base(DeclarativeBase):
    type_annotation_map = {
        str20: String(20),
        str50: String(50),
        str255: String(255),
    }

    description: Mapped[str255|None]
    notes: Mapped[str255|None]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )