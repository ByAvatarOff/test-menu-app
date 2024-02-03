"""
Counters tests
"""
from httpx import AsyncClient
from utils import reverse

from menu_app.dish.dish_router import create_dish
from menu_app.menu.menu_router import create_menu, delete_menu, get_menu, list_menus
from menu_app.submenu.submenu_router import (
    create_submenu,
    delete_submenu,
    get_submenu,
    list_submenus,
)


class TestCreateEntities:
    async def test_create_records(
            self,
            ac: AsyncClient
    ) -> None:
        """Create records for check counters"""
        response_menu = await ac.post(
            await reverse(create_menu),
            json={
                'title': 'My menu 1',
                'description': 'My menu description 1'
            })
        menu_id = response_menu.json().get('id', '')

        response_submenu = await ac.post(
            await reverse(
                create_submenu,
                menu_id=menu_id
            ),
            json={
                'title': 'My submenu 1',
                'description': 'My submenu description 1',
            })
        submenu_id = response_submenu.json().get('id', '')

        await ac.post(
            await reverse(
                create_dish,
                menu_id=menu_id,
                submenu_id=submenu_id
            ),
            json={
                'title': 'My dish 1',
                'description': 'My dish description 1',
                'price': '12.50',
            })

        await ac.post(
            await reverse(
                create_dish,
                menu_id=menu_id,
                submenu_id=submenu_id
            ),
            json={
                'title': 'My dish 2',
                'description': 'My dish description 2',
                'price': '13.50',
            })


class TestCountersInMenuSubmenu:

    async def test_counters_in_menu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Check correct number in counters for menu"""
        response = await ac.get(
            await reverse(
                get_menu,
                menu_id=get_menu_id)
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('submenus_count') == 1
        assert data.get('dishes_count') == 2

    async def test_counters_in_submenu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
    ) -> None:
        """Check correct number in counter for submenu"""
        response = await ac.get(
            await reverse(
                get_submenu,
                menu_id=get_menu_id,
                submenu_id=get_submenu_id
            ))

        assert response.status_code == 200
        data = response.json()
        assert data.get('dishes_count') == 2

    async def test_delete_submenu_success(
            self,
            ac: AsyncClient,
            get_menu_id: str,
            get_submenu_id: str
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
        assert len(data) == 0

    async def test_counters_get_menu_after_delete_success(
            self,
            ac: AsyncClient,
            get_menu_id: str
    ) -> None:
        """Check correct number in counters for menu"""
        response = await ac.get(
            await reverse(
                get_menu,
                menu_id=get_menu_id)
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('submenus_count') == 0
        assert data.get('dishes_count') == 0

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
        assert len(data) == 0
