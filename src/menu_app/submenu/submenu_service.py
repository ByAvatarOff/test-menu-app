"""Submenu service layer"""
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from starlette.responses import JSONResponse

from db.cache_repo import CacheMenuAppKeys, CacheRepository
from menu_app.schemas import (
    SubMenuCreateSchema,
    SubMenuReadSchema,
    SubMenuWithCounterSchema,
)
from menu_app.submenu.submenu_repo import SubmenuRepository
from menu_app.utils import SubmenuConverter


class SubmenuService:
    """Service for menu"""

    def __init__(
            self,
            submenu_repo: SubmenuRepository = Depends(),
            submenu_cache: CacheRepository = Depends(),
            menu_app_name_keys: CacheMenuAppKeys = Depends()
    ) -> None:
        self.submenu_repo = submenu_repo
        self.submenu_cache = submenu_cache
        self.menu_app_name_keys = menu_app_name_keys

    async def get_all_submenus(
            self,
            menu_id: UUID
    ) -> list[SubMenuReadSchema]:
        """Get list submenu"""
        list_submenus_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_list_submenus_key,
            menu_id
        )
        cache_list_submenu = await self.submenu_cache.get(list_submenus_key)

        if cache_list_submenu is not None:
            return await SubmenuConverter.convert_submenus_sequence_to_list_submenus(cache_list_submenu)

        list_submenus = await self.submenu_repo.get_all_submenus(
            menu_id=menu_id
        )
        await self.submenu_cache.set(list_submenus_key, list_submenus)
        return await SubmenuConverter.convert_submenus_sequence_to_list_submenus(list_submenus)

    async def create_submenu(
            self,
            menu_id: UUID,
            submenu_payload: SubMenuCreateSchema,
            background_tasks: BackgroundTasks
    ) -> SubMenuReadSchema:
        """Create menu"""
        submenu = await self.submenu_repo.create_submenu(
            submenu_payload=submenu_payload,
            menu_id=menu_id
        )
        background_tasks.add_task(
            self.submenu_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_submenus_key
        )
        background_tasks.add_task(self.submenu_cache.delete, [
            self.menu_app_name_keys.get_list_menus_nested_key,
        ])
        return submenu

    async def get_submenu(
            self,
            submenu_id: UUID
    ) -> SubMenuWithCounterSchema:
        """Get submenu by id"""
        submenu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_submenu_key,
            submenu_id
        )
        cache_submenu = await self.submenu_cache.get(submenu_key)
        if cache_submenu is not None:
            return await SubmenuConverter.convert_submenu_row_to_schema(cache_submenu)

        submenu = await self.submenu_repo.get_submenu(
            submenu_id=submenu_id
        )
        await self.submenu_cache.set(submenu_key, submenu)
        return await SubmenuConverter.convert_submenu_row_to_schema(submenu)

    async def update_submenu(
            self,
            submenu_id: UUID,
            submenu_payload: SubMenuCreateSchema,
            background_tasks: BackgroundTasks
    ) -> SubMenuReadSchema:
        """Update submenu by id"""
        submenu = await self.submenu_repo.update_submenu(
            submenu_id=submenu_id,
            submenu_payload=submenu_payload
        )
        submenu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_submenu_key,
            submenu_id
        )

        background_tasks.add_task(
            self.submenu_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_submenus_key
        )
        background_tasks.add_task(self.submenu_cache.delete, [
            self.menu_app_name_keys.get_list_menus_nested_key,
            submenu_key
        ])
        return submenu

    async def delete_submenu(
            self,
            submenu_id: UUID,
            menu_id: UUID,
            background_tasks: BackgroundTasks
    ) -> JSONResponse:
        """Delete submenu by id"""
        response = await self.submenu_repo.delete_submenu(
            submenu_id=submenu_id
        )
        submenu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_submenu_key,
            submenu_id
        )
        menu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_menu_key,
            menu_id
        )
        background_tasks.add_task(
            self.submenu_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_dishes_key
        )
        background_tasks.add_task(
            self.submenu_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_submenus_key
        )
        background_tasks.add_task(self.submenu_cache.delete, [
            self.menu_app_name_keys.get_list_menus_nested_key,
            menu_key,
            submenu_key
        ])
        return response
