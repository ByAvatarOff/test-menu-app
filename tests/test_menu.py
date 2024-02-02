from httpx import AsyncClient
import pytest
from sqlalchemy import select
from menu_app.models import Menu
from menu_app.schemas import MenuReadSchema
import uuid


@pytest.fixture
async def get_menu_instance(get_async_session):
    """
    Select Menu first instance
    """

    stmt = select(Menu)
    record = await get_async_session.execute(stmt)
    return record.scalars().first()


async def test_create_menu(ac: AsyncClient):
    """
    Create Menu instance, check response fields
    """

    response = await ac.post("/api/v1/menus", json={
        "title": "string", 
        "description": "string"
        })
    data = response.json()
    assert response.status_code == 201
    assert data.get('id', '')
    assert data.get('title') == 'string'
    assert data.get('description') == 'string'


async def test_failed_entitty_create_menu(ac: AsyncClient):
    """
    Failed create menu with incorrect body (without title)
    """

    response = await ac.post("/api/v1/menus", json={
        "description": "string"
        })
    assert response.status_code == 422


async def test_list_menus(ac: AsyncClient):
    """
    List menus, check response is list, check len response
    """

    response = await ac.get("/api/v1/menus")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


async def test_schema_menus(ac: AsyncClient):
    """
    Check menu schemas in response
    """

    response = await ac.get("/api/v1/menus")
    assert response.status_code == 200
    data = response.json()
    for obj in data:
        assert MenuReadSchema(**obj)


async def test_get_menu(ac: AsyncClient, get_menu_instance: MenuReadSchema):
    """
    One menu, check fields in response without counters fields
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_instance.id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get('id') == str(get_menu_instance.id)
    assert data.get('title') == get_menu_instance.title
    assert data.get('description') == get_menu_instance.description


async def test_not_found_get_menu(ac: AsyncClient):
    """
    Check 404 for one menu
    """

    response = await ac.get(f"/api/v1/menus/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'menu not found'


async def test_patch_menu(ac: AsyncClient, get_menu_instance: MenuReadSchema):
    """
    Update menu, check updated fields
    """

    response = await ac.patch(f"/api/v1/menus/{get_menu_instance.id}", json={
        "title": "new_string", 
        "description": "new_desc"
        })
    assert response.status_code == 200
    data = response.json()
    assert data.get('id') == str(get_menu_instance.id)
    assert data.get('title') == "new_string"
    assert data.get('description') == "new_desc"


async def test_not_found_patch_menu(ac: AsyncClient):
    """
    Check 404 for update menu
    """

    response = await ac.patch(f"/api/v1/menus/{uuid.uuid4()}", json={
        "title": "new_string", 
        "description": "new_desc"
        })
    assert response.status_code == 404
    assert response.json().get('detail') == 'menu not found'    


async def test_failed_entitty_patch_menu(ac: AsyncClient, get_menu_instance: MenuReadSchema):
    """
    Failed update menu with incorrect body description - number
    """

    response = await ac.patch(f"/api/v1/menus/{get_menu_instance.id}", json={
        "title": "new_string", 
        "description": 1246
        })
    assert response.status_code == 422


async def test_delete_menu(ac: AsyncClient, get_menu_instance: MenuReadSchema, get_async_session):
    """
    Delete menu
    """
        
    response = await ac.delete(f"/api/v1/menus/{get_menu_instance.id}")
    assert response.status_code == 200
    assert response.json().get('message') == 'Success delete'

    stmt = select(Menu).where(Menu.id == get_menu_instance.id)
    record = await get_async_session.execute(stmt)
    assert record.scalars().all() == []


async def test_not_found_delete_menu(ac: AsyncClient):
    """
    Check 404 for delete menu
    """

    response = await ac.delete(f"/api/v1/menus/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'menu not found'

