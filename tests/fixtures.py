"""
Pytest fixtures
"""
from typing import AsyncGenerator

import pytest
from conftest import async_session_maker, engine_test
from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from menu_app.models import Base, Dish, Menu, Submenu
from menu_app.schemas import DishReadSchema, MenuReadSchema, SubMenuReadSchema


@pytest.fixture
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async session use async session maker"""
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True, scope='session')
async def prepare_database() -> AsyncGenerator:
    """
    Create tables after connect to database
    Drop tables before end tests
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    """Return async generator async client"""
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture
async def get_menu_instance(
        get_async_session: AsyncSession
):
    """
    Select Menu first instance if exists
    Else create menu instance
    Return menu instance
    """
    stmt = select(Menu)
    record = await get_async_session.execute(stmt)
    menu = record.scalars().first()
    if menu:
        return menu
    stmt = (
        insert(Menu)
        .values(
            title='string',
            description='string'
        )
        .returning(Menu))
    record = await get_async_session.execute(stmt)
    await get_async_session.commit()
    return record.scalars().first()


@pytest.fixture
async def get_menu_id(
        get_menu_instance: MenuReadSchema
) -> str:
    """Get from menu instance menu id"""
    return str(get_menu_instance.id)


@pytest.fixture
async def get_submenu_instance(
        get_async_session: AsyncSession,
        get_menu_id: str
):
    """
    Select Submenu first instance if exists
    Else create submenu instance
    Return menu instance
    """
    stmt = select(Submenu)
    record = await get_async_session.execute(stmt)
    submenu = record.scalars().first()
    if submenu:
        return submenu
    stmt = (
        insert(Submenu).values(
            title='string',
            description='string',
            menu_id=get_menu_id)
        .returning(Submenu))
    record = await get_async_session.execute(stmt)
    await get_async_session.commit()
    return record.scalars().first()


@pytest.fixture
async def get_submenu_id(
        get_submenu_instance: SubMenuReadSchema
) -> str:
    """Get from submenu instance submenu id"""
    return str(get_submenu_instance.id)


@pytest.fixture
async def get_dish_instance(
        get_async_session: AsyncSession
) -> DishReadSchema:
    """Select Dish first instance"""
    stmt = select(Dish)
    record = await get_async_session.execute(stmt)
    return record.scalars().first()


@pytest.fixture
async def get_dish_id(
        get_dish_instance: DishReadSchema
) -> str:
    """Select Dish first instance"""
    return str(get_dish_instance.id)
