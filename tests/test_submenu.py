"""
Submenu tests
"""
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils import reverse

from menu_app.menu.menu_router import delete_menu
from menu_app.models import Submenu
from menu_app.schemas import SubMenuReadSchema
from menu_app.submenu.submenu_router import (
    create_submenu,
    delete_submenu,
    get_submenu,
    list_submenus,
    update_submenu,
)


class TestCreateSubmenu:

    async def test_create_submenu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Create Submenu instance, check response fields"""
        response = await ac.post(
            await reverse(
                create_submenu,
                menu_id=get_menu_id
            ),
            json={
                'title': 'string',
                'description': 'string',
            })
        data = response.json()
        assert response.status_code == 201
        assert data.get('id', '')
        assert data.get('title') == 'string'
        assert data.get('description') == 'string'

    async def test_create_submenu_entity_failed(
            self,
            ac: AsyncClient,
            get_menu_id
    ) -> None:
        """Failed create submenu with incorrect body (without title)"""
        response = await ac.post(
            await reverse(
                create_submenu,
                menu_id=get_menu_id
            ),
            json={
                'description': 'string',
            })
        assert response.status_code == 422


class TestListSubmenu:
    async def test_list_submenus_success(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """List submenus, check response is list, check len response"""
        response = await ac.get(
            await reverse(
                list_submenus,
                menu_id=get_menu_id
            ))
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    async def test_schema_submenus_success(
            self,
            ac: AsyncClient,
            get_menu_id
    ):
        """Check submenu schemas in response"""
        response = await ac.get(
            await reverse(
                list_submenus,
                menu_id=get_menu_id
            ))
        assert response.status_code == 200
        data = response.json()
        for obj in data:
            assert SubMenuReadSchema(**obj)


class TestGetSubmenu:

    async def test_get_submenu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_instance: SubMenuReadSchema
    ) -> None:
        """One submenu, check fields in response without counter field"""
        response = await ac.get(
            await reverse(
                get_submenu,
                menu_id=get_menu_id,
                submenu_id=get_submenu_instance.id
            ))
        assert response.status_code == 200
        data = response.json()
        assert data.get('id') == str(get_submenu_instance.id)
        assert data.get('title') == get_submenu_instance.title
        assert data.get('description') == get_submenu_instance.description

    async def test_get_submenu_not_found_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Check 404 for one submenu"""
        response = await ac.get(
            await reverse(
                get_submenu,
                menu_id=get_menu_id,
                submenu_id=uuid4()
            ))
        assert response.status_code == 404
        assert response.json().get('detail') == 'submenu not found'


class TestUpdateSubmenu:
    async def test_patch_submenu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Update submenu, check updated fields"""
        response = await ac.patch(
            await reverse(
                update_submenu,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc'
            })
        assert response.status_code == 200
        data = response.json()
        assert data.get('id') == str(get_submenu_id)
        assert data.get('title') == 'new_string'
        assert data.get('description') == 'new_desc'

    async def test_patch_submenu_not_found_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Check 404 for update submenu"""
        response = await ac.patch(
            await reverse(
                update_submenu,
                menu_id=get_menu_id,
                submenu_id=uuid4()
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc'
            })
        assert response.status_code == 404
        assert response.json().get('detail') == 'submenu not found'

    async def test_exists_title_patch_menu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Check 404 for update menu"""
        response = await ac.patch(
            await reverse(
                update_submenu,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ),
            json={
                'title': 'new_string',
                'description': 'new_desc'
            })
        assert response.status_code == 400
        assert response.json().get('detail') == 'Submenu with get title exists'

    async def test_patch_submenu_entity_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Failed update submenu with incorrect body description - number"""
        response = await ac.patch(
            await reverse(
                update_submenu,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ),
            json={
                'title': 'new_string',
                'description': 1234
            })
        assert response.status_code == 422


class TestDeleteSubmenu:

    async def test_delete_submenu_not_found_failed(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Check 404 to submenu for delete submenu"""
        response = await ac.delete(
            await reverse(
                delete_submenu,
                menu_id=get_menu_id,
                submenu_id=uuid4()
            ))
        assert response.status_code == 404
        assert response.json().get('detail') == 'submenu not found'

    async def test_delete_submenu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str,
            get_async_session: AsyncSession
    ) -> None:
        """Delete submenu"""
        response = await ac.delete(
            await reverse(
                delete_submenu,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ))
        assert response.status_code == 200
        assert response.json().get('message') == 'Success submenu delete'
        stmt = select(Submenu).where(Submenu.id == get_submenu_id)
        record = await get_async_session.execute(stmt)
        assert record.scalars().all() == []


class TestCleanMenuInSubmenu:
    async def test_delete_menu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Delete menu"""
        response = await ac.delete(
            await reverse(
                delete_menu,
                menu_id=get_menu_id,
            ))
        assert response.status_code == 200
        assert response.json().get('message') == 'Success menu delete'
