"""
Menu tests
"""
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils import reverse

from menu_app.menu.menu_router import (
    create_menu,
    delete_menu,
    get_menu,
    list_menus,
    update_menu,
)
from menu_app.models import Menu
from menu_app.schemas import MenuReadSchema


class TestCreateMenu:
    async def test_create_menu_success(
            self,
            ac: AsyncClient
    ) -> None:
        """Create Menu instance, check response fields"""

        response = await ac.post(
            await reverse(create_menu),
            json={
                'title': 'string',
                'description': 'string'
            })
        data = response.json()
        assert response.status_code == 201
        assert data.get('id', '')
        assert data.get('title') == 'string'
        assert data.get('description') == 'string'

    async def test_create_menu_entity_failed(
            self,
            ac: AsyncClient
    ) -> None:
        """Failed create menu with incorrect body (without title)"""
        response = await ac.post(
            await reverse(create_menu),
            json={
                'description': 'string'
            })
        assert response.status_code == 422


class TestListMenu:
    async def test_list_menus_success(
            self,
            ac: AsyncClient
    ) -> None:
        """List menus, check response is list, check len response"""
        response = await ac.get(
            await reverse(list_menus)
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    async def test_schema_menus_success(
            self,
            ac: AsyncClient
    ) -> None:
        """Check menu schemas in response"""
        response = await ac.get(
            await reverse(list_menus)
        )
        assert response.status_code == 200
        data = response.json()
        for obj in data:
            assert MenuReadSchema(**obj)


class TestGetMenu:
    async def test_get_menu_success(
            self,
            ac: AsyncClient,
            get_menu_instance: MenuReadSchema
    ) -> None:
        """One menu, check fields in response without counters fields"""
        response = await ac.get(
            await reverse(
                get_menu,
                menu_id=get_menu_instance.id)
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('id') == str(get_menu_instance.id)
        assert data.get('title') == get_menu_instance.title
        assert data.get('description') == get_menu_instance.description

    async def test_get_menu_not_found_failed(
            self,
            ac: AsyncClient
    ) -> None:
        """Check 404 for one menu"""
        response = await ac.get(
            await reverse(
                get_menu,
                menu_id=uuid4())
        )
        assert response.status_code == 404
        assert response.json().get('detail') == 'menu not found'


class TestUpdateMenu:
    async def test_patch_menu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Update menu, check updated fields"""

        response = await ac.patch(
            await reverse(
                update_menu,
                menu_id=get_menu_id
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc'
            })
        assert response.status_code == 200
        data = response.json()
        assert data.get('id') == str(get_menu_id)
        assert data.get('title') == 'new_string'
        assert data.get('description') == 'new_desc'

    async def test_patch_menu_not_found_failed(
            self,
            ac: AsyncClient
    ) -> None:
        """Check 404 for update menu"""
        response = await ac.patch(
            await reverse(
                update_menu,
                menu_id=uuid4()
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc'
            })
        assert response.status_code == 404
        assert response.json().get('detail') == 'menu not found'

    async def test_patch_menu_entity_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Failed update menu with incorrect body description - number"""
        response = await ac.patch(
            await reverse(
                update_menu,
                menu_id=get_menu_id
            ),
            json={
                'title': 'new_string',
                'description': 1246
            })
        assert response.status_code == 422


class TestDeleteMenu:
    async def test_delete_menu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_async_session: AsyncSession
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
        stmt = select(Menu).where(Menu.id == get_menu_id)
        record = await get_async_session.execute(stmt)
        assert record.scalars().all() == []

    async def test_delete_menu_not_found_failed(
            self,
            ac: AsyncClient
    ) -> None:
        """Check 404 for delete menu"""
        response = await ac.delete(
            await reverse(
                delete_menu,
                menu_id=uuid4()
            )
        )
        assert response.status_code == 404
        assert response.json().get('detail') == 'menu not found'
