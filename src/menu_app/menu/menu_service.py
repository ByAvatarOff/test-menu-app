"""Menu service layer"""
from uuid import UUID

from fastapi import Depends
from starlette.responses import JSONResponse

from db.cache_repo import CacheMenuAppKeys, CacheRepository
from menu_app.menu.menu_repo import MenuRepository
from menu_app.schemas import MenuCreateSchema, MenuReadSchema, MenuWithCounterSchema
from menu_app.utils import MenuConverter


class MenuService:
    """Service for menu"""

    def __init__(
            self,
            menu_repo: MenuRepository = Depends(),
            menu_cache: CacheRepository = Depends(),
            menu_app_name_keys: CacheMenuAppKeys = Depends()
    ) -> None:
        self.menu_repo = menu_repo
        self.menu_cache = menu_cache
        self.menu_app_name_keys = menu_app_name_keys

    async def get_all_menus(
            self
    ) -> list[MenuReadSchema]:
        """Get list menu"""
        cache_list_menu = await self.menu_cache.get(self.menu_app_name_keys.get_list_menus_key)

        if cache_list_menu is not None:
            return await MenuConverter.convert_menus_sequence_to_list_menus(cache_list_menu)

        list_menus = await self.menu_repo.get_all_menus()
        await self.menu_cache.set(self.menu_app_name_keys.get_list_menus_key, list_menus)
        return await MenuConverter.convert_menus_sequence_to_list_menus(list_menus)

    async def create_menu(
            self,
            menu_payload: MenuCreateSchema
    ) -> MenuReadSchema:
        """Create menu"""
        menu = await self.menu_repo.create_menu(
            menu_payload=menu_payload
        )
        await self.menu_cache.delete(self.menu_app_name_keys.get_list_menus_key)
        return menu

    async def get_menu(
            self,
            menu_id: UUID
    ) -> MenuWithCounterSchema:
        """Get menu by id"""
        menu = await self.menu_repo.get_menu(
            menu_id=menu_id
        )
        return await MenuConverter.convert_menu_row_to_schema(menu)

    async def update_menu(
            self,
            menu_id: UUID,
            menu_payload: MenuCreateSchema
    ) -> MenuReadSchema:
        """Update menu by id"""
        menu = await self.menu_repo.update_menu(
            menu_id=menu_id,
            menu_payload=menu_payload
        )
        await self.menu_cache.delete(self.menu_app_name_keys.get_list_menus_key)
        return menu

    async def delete_menu(
            self,
            menu_id: UUID
    ) -> JSONResponse:
        """Delete menu by id"""
        response = await self.menu_repo.delete_menu(
            menu_id=menu_id
        )
        await self.menu_cache.delete(
            self.menu_app_name_keys.get_list_menus_key,
            self.menu_app_name_keys.get_list_submenus_key,
            self.menu_app_name_keys.get_list_dishes_key
        )
        return response