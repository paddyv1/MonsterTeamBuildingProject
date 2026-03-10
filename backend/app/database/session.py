from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncIterator


engine = create_async_engine("postgresql+asyncpg://app:app@db:5432/app", echo=False)


Session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    FastAPI dependency that provides an AsyncSession per request.

    Pattern:
      - open session
      - yield it to the endpoint
      - commit if no exception
      - rollback if exception
      - close session
    """
    async with Session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
