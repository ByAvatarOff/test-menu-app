"""Menu service layer"""
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from starlette.responses import JSONResponse

from db.cache_repo import CacheMenuAppKeys, CacheRepository
from menu_app.menu.menu_repo import MenuRepository
from menu_app.schemas import MenuCreateSchema, MenuReadSchema, MenuWithCounterSchema
from menu_app.utils import MenuConverter, add_discount_to_dish


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

    async def list_menus_with_nested_obj(
            self
    ):
        """list menus with nested obj"""
        cache_list_menu = await self.menu_cache.get(self.menu_app_name_keys.get_list_menus_nested_key)
        dishes_discount = await self.menu_cache.get(self.menu_app_name_keys.get_dish_discount_key)

        if cache_list_menu is not None:
            return await add_discount_to_dish(cache_list_menu, dishes_discount)

        list_menus_nested = await self.menu_repo.get_all_menus_with_nested_obj()
        await self.menu_cache.set(self.menu_app_name_keys.get_list_menus_nested_key, list_menus_nested)
        return await add_discount_to_dish(list_menus_nested, dishes_discount)

    async def create_menu(
            self,
            menu_payload: MenuCreateSchema,
            background_tasks: BackgroundTasks,
    ) -> MenuReadSchema:
        """Create menu"""
        menu = await self.menu_repo.create_menu(
            menu_payload=menu_payload
        )

        background_tasks.add_task(self.menu_cache.delete, [
            self.menu_app_name_keys.get_list_menus_nested_key,
        ])
        background_tasks.add_task(
            self.menu_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_menus_key
        )
        return menu

    async def get_menu(
            self,
            menu_id: UUID
    ) -> MenuWithCounterSchema:
        """Get menu by id"""
        menu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_menu_key,
            menu_id
        )
        cache_menu = await self.menu_cache.get(menu_key)
        if cache_menu is not None:
            return await MenuConverter.convert_menu_row_to_schema(cache_menu)

        menu = await self.menu_repo.get_menu(
            menu_id=menu_id
        )
        await self.menu_cache.set(menu_key, menu)
        return await MenuConverter.convert_menu_row_to_schema(menu)

    async def update_menu(
            self,
            menu_id: UUID,
            menu_payload: MenuCreateSchema,
            background_tasks: BackgroundTasks,
    ) -> MenuReadSchema:
        """Update menu by id"""
        menu = await self.menu_repo.update_menu(
            menu_id=menu_id,
            menu_payload=menu_payload
        )
        menu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_menu_key,
            menu_id
        )

        background_tasks.add_task(self.menu_cache.delete, [
            self.menu_app_name_keys.get_list_menus_nested_key,
            menu_key
        ])

        background_tasks.add_task(
            self.menu_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_menus_key
        )
        return menu

    async def delete_menu(
            self,
            menu_id: UUID,
            background_tasks: BackgroundTasks
    ) -> JSONResponse:
        """Delete menu by id"""
        response = await self.menu_repo.delete_menu(
            menu_id=menu_id
        )
        menu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_menu_key,
            menu_id
        )
        background_tasks.add_task(
            self.menu_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_common_key
        )
        background_tasks.add_task(self.menu_cache.delete, [menu_key])

        return response
