from httpx import AsyncClient
import pytest
from sqlalchemy import select
from menu_app.models import Submenu, Menu


async def test_create_records(ac: AsyncClient):
    """
    Create records for check counters
    """

    response = await ac.post("/api/v1/menus", json={
        "title": "My menu 1", 
        "description": "My menu description 1"
        })
    menu_id = response.json().get('id', '')

    response = await ac.post(f"/api/v1/menus/{menu_id}/submenus", json={
        "title": "My submenu 1", 
        "description": "My submenu description 1",
        })
    submenu_id = response.json().get('id', '')

    await ac.post(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", json={
        "title": "My dish 1", 
        "description": "My dish description 1",
        "price": "12.50",
        })
    await ac.post(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", json={
        "title": "My dish 2", 
        "description": "My dish description 2",
        "price": "13.50",
        })


@pytest.fixture
async def get_menu_id(get_async_session):
    """
    Select menu first instance
    If not exists create records
    Return menu id
    """
    
    stmt = select(Menu)
    record = await get_async_session.execute(stmt)
    return record.scalars().first().id


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
    assert data.get('submenus_count') == 1
    assert data.get('dishes_count') == 2


async def test_counters_get_submenu(ac: AsyncClient, get_menu_id: str, get_submenu_id: str):
    """
    Check correct number in counter for submenu
    """
        
    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data.get('dishes_count') == 2


async def test_delete_submenu(ac: AsyncClient, get_menu_id: str, get_submenu_id: str):
    """
    Delete submenu
    """
    response = await ac.delete(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}")
    assert response.status_code == 200
    assert response.json().get('message') == 'Success delete'


async def test_list_submenus(ac: AsyncClient, get_menu_id: str):
    """
    List submenus, check response is list, check len response
    """
        
    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


async def test_counters_get_menu_after_delete(ac: AsyncClient, get_menu_id: str):
    """
    Check correct number in counters for menu
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get('submenus_count') == 0
    assert data.get('dishes_count') == 0


async def test_delete_menu(ac: AsyncClient, get_menu_id: str):
    """
    Delete menu
    """
        
    response = await ac.delete(f"/api/v1/menus/{get_menu_id}")
    assert response.status_code == 200
    assert response.json().get('message') == 'Success delete'


async def test_list_menus(ac: AsyncClient):
    """
    List menus, check response is list, check len response
    """

    response = await ac.get("/api/v1/menus")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0