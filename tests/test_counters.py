from httpx import AsyncClient
import pytest
from sqlalchemy import select, insert
from menu.models import Submenu, Menu, Dish


async def create_records(get_async_session):
    """
    Create records for check counters
    """

    stmt = insert(Menu).values(title='string', description='string').returning(Menu)
    menu_record = await get_async_session.execute(stmt)
    menu_id = menu_record.scalars().first().id

    submenu_data = [
        {"title": 'string1', "description": 'string1', "menu_id": menu_id},
        {"title": 'string2', "description": 'string2', "menu_id": menu_id}
    ]
    sumbenu_stmt = insert(Submenu).values(submenu_data).returning(Submenu)
    submenu_record = await get_async_session.execute(sumbenu_stmt)
    submenu_id = submenu_record.scalars().all()
    dishes_data = [
        {"title": 'string1', "description": 'string1', "price": "12.77", "submenu_id": submenu_id[0].id},
        {"title": 'string2', "description": 'string2', "price": "12.77", "submenu_id": submenu_id[0].id},
        {"title": 'string3', "description": 'string3', "price": "12.77", "submenu_id": submenu_id[0].id},
        {"title": 'string4', "description": 'string4', "price": "12.77", "submenu_id": submenu_id[1].id}
    ]
    dish_stmt = insert(Dish).values(dishes_data).returning(Dish)
    await get_async_session.execute(dish_stmt)

    await get_async_session.commit()
    return menu_id


@pytest.fixture
async def get_menu_id(get_async_session):
    """
    Select menu first instance
    If not exists create records
    Return menu id
    """
    
    stmt = select(Menu)
    record = await get_async_session.execute(stmt)
    menu = record.scalars().first()
    if menu is None:
        return await create_records(get_async_session)
    return menu.id


@pytest.fixture
async def get_submenu_id(get_async_session):
    """
    Select submenu first instance
    Return submenu id
    """

    stmt = select(Submenu)
    record = await get_async_session.execute(stmt)
    return record.scalars().first().id


async def test_counters_get_menu(ac: AsyncClient, get_menu_id: str):
    """
    Check correct number in counters for menu
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get('submenus_count') == 2
    assert data.get('dishes_count') == 4


async def test_counters_get_submenu(ac: AsyncClient, get_menu_id: str, get_submenu_id: str, get_async_session):
    """
    Check correct number in counter for submenu
    """
        
    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data.get('dishes_count') == 3


async def test_delete_menu(ac: AsyncClient, get_menu_id: str):
    """
    Delete menu
    """
        
    response = await ac.delete(f"/api/v1/menus/{get_menu_id}")
    assert response.status_code == 200
    assert response.json().get('message') == 'Success delete'