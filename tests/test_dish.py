from httpx import AsyncClient
import pytest
from sqlalchemy import select, insert
from menu.models import Submenu, Menu, Dish
from menu.schemas import DishReadSchema
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
async def get_submenu_id(get_async_session, get_menu_id: str):
    """
    Select Subenu first instance if exists
    Else create submenu instanse 
    Return menu id
    """

    stmt = select(Submenu)
    record = await get_async_session.execute(stmt)
    res = record.scalars().first()
    if res:
        return res.id
    
    stmt = insert(Submenu).values(title='string', description='string', menu_id=get_menu_id).returning(Submenu)
    record = await get_async_session.execute(stmt)
    await get_async_session.commit()
    return record.scalars().first().id


@pytest.fixture
async def get_dish_instance(get_async_session):
    """
    Select Dish first instance
    """

    stmt = select(Dish)
    record = await get_async_session.execute(stmt)
    return record.scalars().first()


async def test_create_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str):
    """
    Create Dish instance, check response fields
    """

    response = await ac.post(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes", json={
        "title": "string", 
        "description": "string",
        "price": "12.389",
        })
    data = response.json()
    assert response.status_code == 201
    assert data.get('id', '')
    assert data.get('title') == 'string'
    assert data.get('description') == 'string'
    assert data.get('price') == '12.39'


async def test_failed_entitty_create_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str):
    """
    Failed create dish with incorrect body (without title and price)
    """
        
    response = await ac.post(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes", json={
        "description": "string"
        })
    assert response.status_code == 422


async def test_list_dishes(ac: AsyncClient, get_menu_id: str, get_submenu_id: str):
    """
    List dishes, check response is list, check len response
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1


async def test_schema_dishes(ac: AsyncClient, get_menu_id: str, get_submenu_id: str):
    """
    Check dish schemas in response
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes")
    assert response.status_code == 200
    data = response.json()
    for obj in data:
        assert DishReadSchema(**obj)


async def test_get_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str, get_dish_instance: DishReadSchema):
    """
    One dish, check fields in response
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{get_dish_instance.id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get('id') == str(get_dish_instance.id)
    assert data.get('title') == get_dish_instance.title
    assert data.get('description') == get_dish_instance.description
    assert data.get('price') == '12.39'


async def test_not_found_get_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str):
    """
    Check 404 for one dish
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'dish not found'


async def test_not_found_get_submenu(ac: AsyncClient, get_menu_id: str, get_dish_instance: DishReadSchema):
    """
    Check 404 for one submenu
    """

    response = await ac.get(f"/api/v1/menus/{get_menu_id}/submenus/{uuid.uuid4()}/dishes/{get_dish_instance.id}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'submenu not found'


async def test_patch_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str, get_dish_instance: DishReadSchema):
    """
    Update dish, check updated fields
    """

    response = await ac.patch(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{get_dish_instance.id}", json={
        "title": "new_string", 
        "description": "new_desc",
        "price": "12.91111"
        })
    
    assert response.status_code == 200
    data = response.json()
    assert data.get('id') == str(get_dish_instance.id)
    assert data.get('title') == "new_string"
    assert data.get('description') == "new_desc"
    assert data.get('price') == "12.91"


async def test_not_found_patch_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str,):
    """
    Check 404 for update dish
    """

    response = await ac.patch(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{uuid.uuid4()}", json={
        "title": "new_string", 
        "description": "new_desc",
        "price": "12.91111"
        })
    assert response.status_code == 404
    assert response.json().get('detail') == 'dish not found'   


async def test_not_found_patch_submenu(ac: AsyncClient, get_menu_id: str, get_dish_instance: DishReadSchema):
    """
    Check 404 for update submenu
    """

    response = await ac.patch(f"/api/v1/menus/{get_menu_id}/submenus/{uuid.uuid4()}/dishes/{get_dish_instance.id}", json={
        "title": "new_string", 
        "description": "new_desc",
        "price": "12.91111"
        })
    assert response.status_code == 404
    assert response.json().get('detail') == 'submenu not found'


async def test_failed_entitty_patch_submenu(ac: AsyncClient, get_menu_id: str, get_submenu_id: str, get_dish_instance: DishReadSchema):
    """
    Failed update dish without field price and description - number
    """

    response = await ac.patch(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{get_dish_instance.id}", json={
        "title": "new_string", 
        "description": 1246
        })
    assert response.status_code == 422


async def test_incorrect_price_patch_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str, get_dish_instance: DishReadSchema):
    """
    Failed update dish with incorrect type price
    """
        
    response = await ac.patch(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{get_dish_instance.id}", json={
        "title": "new_string", 
        "description": 1246,
        "price": "12n.911f11"
        })
    assert response.status_code == 422


async def test_not_found_delete_submenu(ac: AsyncClient, get_menu_id: str, get_dish_instance: DishReadSchema):
    """
    Check 404 to submenu for delete submenu
    """

    response = await ac.delete(f"/api/v1/menus/{get_menu_id}/submenus/{uuid.uuid4()}/dishes/{get_dish_instance.id}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'submenu not found'


async def test_not_found_delete_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str):
    """
    Check 404 to submenu for delete dish
    """

    response = await ac.delete(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json().get('detail') == 'dish not found'


async def test_delete_dish(ac: AsyncClient, get_menu_id: str, get_submenu_id: str, get_dish_instance: DishReadSchema, get_async_session):
    """
    Delete submenu
    """
        
    response = await ac.delete(f"/api/v1/menus/{get_menu_id}/submenus/{get_submenu_id}/dishes/{get_dish_instance.id}")
    assert response.status_code == 200
    assert response.json().get('message') == 'Success delete'

    stmt = select(Dish).where(Dish.id == get_dish_instance.id)
    record = await get_async_session.execute(stmt)
    assert record.scalars().all() == []


async def test_delete_menu(ac: AsyncClient, get_menu_id: str):
    """
    Delete menu
    """
        
    response = await ac.delete(f"/api/v1/menus/{get_menu_id}")
    assert response.status_code == 200
    assert response.json().get('message') == 'Success delete'
