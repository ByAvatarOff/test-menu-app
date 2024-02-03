"""
Create async connection to database
"""
from typing import AsyncGenerator

from redis import asyncio as aioredis
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, REDIS_HOST, REDIS_PORT

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    create async session maker and return session object
    """
    async with async_session_maker() as session:
        yield session


async def get_redis_session() -> AsyncGenerator[Redis, None]:
    """
    create async session maker and return session object with Redis connection
    """
    async with aioredis.from_url(f'redis://{REDIS_HOST}:{REDIS_PORT}/0') as redis_session:
        yield redis_session
