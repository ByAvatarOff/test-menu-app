"""
Dish tests
"""
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils import reverse

from menu_app.dish.dish_router import (
    create_dish,
    delete_dish,
    get_dish,
    list_dishes,
    update_dish,
)
from menu_app.menu.menu_router import delete_menu
from menu_app.models import Dish
from menu_app.schemas import DishReadSchema


class TestCreateDish:
    async def test_create_dish_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Create Dish instance, check response fields"""
        response = await ac.post(
            await reverse(
                create_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ),
            json={
                'title': 'string',
                'description': 'string',
                'price': '12.389'
            })
        data = response.json()
        assert response.status_code == 201
        assert data.get('id', '')
        assert data.get('title') == 'string'
        assert data.get('description') == 'string'
        assert data.get('price') == '12.39'

    async def test_create_dish_entity_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Failed create dish with incorrect body (without title and price)"""
        response = await ac.post(
            await reverse(
                create_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ),
            json={
                'description': 'string',
            })
        assert response.status_code == 422


class TestListDish:
    async def test_list_dishes_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """List dishes, check response is list, check len response"""
        response = await ac.get(
            await reverse(
                list_dishes,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    async def test_schema_dishes_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Check dish schemas in response"""
        response = await ac.get(
            await reverse(
                list_dishes,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ))
        assert response.status_code == 200
        data = response.json()
        for obj in data:
            assert DishReadSchema(**obj)


class TestGetDish:

    async def test_get_dish_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str,
            get_dish_instance: DishReadSchema
    ) -> None:
        """One dish, check fields in response"""
        response = await ac.get(
            await reverse(
                get_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id,
                dish_id=get_dish_instance.id
            ))
        assert response.status_code == 200
        data = response.json()
        assert data.get('id') == str(get_dish_instance.id)
        assert data.get('title') == get_dish_instance.title
        assert data.get('description') == get_dish_instance.description
        assert data.get('price') == '12.39'

    async def test_get_dish_not_found_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Check 404 for one dish"""
        response = await ac.get(
            await reverse(
                get_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id,
                dish_id=uuid4()
            ))
        assert response.status_code == 404
        assert response.json().get('detail') == 'dish not found'


class TestUpdateDish:
    async def test_patch_dish_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str,
            get_dish_instance: DishReadSchema
    ) -> None:
        """Update dish, check updated fields"""
        response = await ac.patch(
            await reverse(
                update_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id,
                dish_id=get_dish_instance.id
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc',
                'price': '12.91111'
            })
        assert response.status_code == 200
        data = response.json()
        assert data.get('id') == str(get_dish_instance.id)
        assert data.get('title') == 'new_string'
        assert data.get('description') == 'new_desc'
        assert data.get('price') == '12.91'

    async def test_patch_dish_not_found_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Check 404 for update dish"""
        response = await ac.patch(
            await reverse(
                update_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id,
                dish_id=uuid4()
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc',
                'price': '12.91111'
            })
        assert response.status_code == 404
        assert response.json().get('detail') == 'dish not found'

    async def test_patch_submenu_entity_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str,
            get_dish_id: str
    ) -> None:
        """Failed update dish without field price and description - number"""
        response = await ac.patch(
            await reverse(
                update_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id,
                dish_id=get_dish_id
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc',
            })
        assert response.status_code == 422

    async def test_price_patch_dish_incorrect_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str,
            get_dish_id: str
    ) -> None:
        """Failed update dish with incorrect type price"""
        response = await ac.patch(
            await reverse(
                update_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id,
                dish_id=get_dish_id
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc',
                'price': '12n.911f11'
            })
        assert response.status_code == 422


class TestDeleteDish:
    async def test_delete_dish_not_found_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Check 404 to submenu for delete dish"""
        response = await ac.delete(
            await reverse(
                delete_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id,
                dish_id=uuid4()
            ))
        assert response.status_code == 404
        assert response.json().get('detail') == 'dish not found'

    async def test_delete_dish_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str,
            get_dish_id: DishReadSchema,
            get_async_session: AsyncSession):
        """Delete submenu"""
        response = await ac.delete(
            await reverse(
                delete_dish,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id,
                dish_id=get_dish_id
            ))
        assert response.status_code == 200
        assert response.json().get('message') == 'Success dish delete'
        stmt = select(Dish).where(Dish.id == get_dish_id)
        record = await get_async_session.execute(stmt)
        assert record.scalars().all() == []


class TestCleanMenuInDish:
    async def test_delete_menu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Delete menu"""
        response = await ac.delete(
            await reverse(
                delete_menu,
                menu_id=get_menu_id
            )
        )
        assert response.status_code == 200
        assert response.json().get('message') == 'Success menu delete'
