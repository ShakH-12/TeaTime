from sqlalchemy import (
    select, update, delete,
    DateTime, func, ForeignKey
)
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship, joinedload
)

engine = create_async_engine("sqlite+aiosqlite:///data.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
	async with new_session() as session:
		yield session


class Base(DeclarativeBase):
	pass


async def create_tables():
	async with engine.begin() as conn:
		# await conn.run_sync(Base.metadata.drop_all)
		await conn.run_sync(Base.metadata.create_all)

