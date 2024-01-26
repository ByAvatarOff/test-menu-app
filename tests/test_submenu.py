from httpx import AsyncClient
import pytest
from sqlalchemy import select, insert
from menu.models import Submenu, Menu
from menu.schemas import SubMenuReadSchema
import uuid


@pytest.fixture
async def get_menu_id(get_async_session):
    """
    Select Menu first instance if exists
    Else create menu instanse 
    Return menu id
    """
    stmt = select(Menu)
    record = await get_async_session.execute(stmt)
    res = record.scalars().first()
    
    if res:
        return res.id
    
    stmt = insert(Menu).values(title='string', description='string').returning(Menu)
    record = await get_async_session.execute(stmt)
    await get_async_session.commit()
    return record.scalars().first().id


@pytest.fixture
async def get_submenu_instance(get_async_session):
    """
    Select Menu first instance
    """

    stmt = select(Submenu)
    record = await get_async_session.execute(stmt)
    return record.scalars().first()


async def test_create_submenu(ac: AsyncClient, get_menu_id: str):
    """
    Create Submenu instance, check response fields
    """
        
    response = await ac.post(f"/api/v1/menus/{get_menu_id}/submenus", json={
        "title": "string", 
        "description": "string",
        })
    data = response.json()
    assert response.status_code == 201
    assert data.get('id', '')
    assert data.get('title') == 'string'
    assert data.get('description') == 'string'


async def test_failed_entitty_create_submenu(ac: AsyncClient, get_menu_id: str):
    """
    Failed create submenu with incorrect body (without title)
    """
        
    response = await ac.post(f"/api/v1/menus/{get_menu_id}/submenus", json={
        "description": "string"
        })
    assert response.status_code == 422


async def test_list_submenus(ac: AsyncClient, get_menu_id: str):
    """
    List submenus, check response is list, check len response
    """
        
    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


async def test_schema_submenus(ac: AsyncClient, get_menu_id: str):
    """
    Check submenu schemas in response
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus")
    assert response.status_code == 200
    data = response.json()
    for obj in data:
        assert SubMenuReadSchema(**obj)


async def test_get_submenu(ac: AsyncClient, get_menu_id: str, get_submenu_instance: SubMenuReadSchema):
    """
    One submenu, check fields in response without counter field
    """
        
    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_instance.id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get('id') == str(get_submenu_instance.id)
    assert data.get('title') == get_submenu_instance.title
    assert data.get('description') == get_submenu_instance.description


async def test_not_found_get_submenu(ac: AsyncClient, get_menu_id: str):
    """
    Check 404 for one submenu
    """
        
    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'submenu not found'


async def test_not_found_get_menu(ac: AsyncClient, get_submenu_instance: SubMenuReadSchema):
    """
    Check 404 for one menu
    """

    response = await ac.get(f"/api/v1/menus/{uuid.uuid4()}/submenus/{get_submenu_instance.id}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'menu not found'


async def test_patch_submenu(ac: AsyncClient, get_menu_id: str, get_submenu_instance: SubMenuReadSchema):
    """
    Update submenu, check updated fields
    """

    response = await ac.patch(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_instance.id}", json={
        "title": "new_string", 
        "description": "new_desc"
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data.get('id') == str(get_submenu_instance.id)
    assert data.get('title') == "new_string"
    assert data.get('description') == "new_desc"


async def test_not_found_patch_submenu(ac: AsyncClient, get_menu_id: str):
    """
    Check 404 for update submenu
    """
        
    response = await ac.patch(f"/api/v1/menus/{get_menu_id}/submenus/{uuid.uuid4()}", json={
        "title": "new_string", 
        "description": "new_desc"
        })
    assert response.status_code == 404
    assert response.json().get('detail') == 'submenu not found'   


async def test_not_found_patch_menu(ac: AsyncClient, get_submenu_instance: SubMenuReadSchema):
    """
    Check 404 for update menu
    """
        
    response = await ac.patch(f"/api/v1/menus/{uuid.uuid4()}/submenus/{get_submenu_instance.id}", json={
        "title": "new_string", 
        "description": "new_desc"
        })
    assert response.status_code == 404
    assert response.json().get('detail') == 'menu not found'


async def test_failed_entitty_patch_submenu(ac: AsyncClient, get_menu_id: str, get_submenu_instance: SubMenuReadSchema):
    """
    Failed update submenu with incorrect body description - number
    """

    response = await ac.patch(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_instance.id}", json={
        "title": "new_string", 
        "description": 1246
        })
    assert response.status_code == 422


async def test_not_found_delete_submenu(ac: AsyncClient, get_menu_id: str):
    """
    Check 404 to submenu for delete submenu
    """

    response = await ac.delete(f"/api/v1/menus/{get_menu_id}/submenus/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'submenu not found'


async def test_not_found_delete_menu(ac: AsyncClient, get_submenu_instance: SubMenuReadSchema):
    """
    Check 404 to menu for delete submenu
    """

    response = await ac.delete(f"/api/v1/menus/{uuid.uuid4()}/submenus/{get_submenu_instance.id}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'menu not found'


async def test_delete_submenu(ac: AsyncClient, get_menu_id: str, get_submenu_instance: SubMenuReadSchema, get_async_session):
    """
    Delete submenu
    """

    response = await ac.delete(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_instance.id}")
    assert response.status_code == 200
    assert response.json().get('message') == 'Success delete'

    stmt = select(Submenu).where(Submenu.id == get_submenu_instance.id)
    record = await get_async_session.execute(stmt)
    assert record.scalars().all() == []


async def test_delete_menu(ac: AsyncClient, get_menu_id: str):
    """
    Delete menu
    """
        
    response = await ac.delete(f"/api/v1/menus/{get_menu_id}")
    assert response.status_code == 200
    assert response.json().get('message') == 'Success delete'
