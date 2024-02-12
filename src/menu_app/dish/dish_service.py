"""DIsh service layer"""
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from starlette.responses import JSONResponse

from db.cache_repo import CacheMenuAppKeys, CacheRepository
from menu_app.dish.dish_repo import DishRepository
from menu_app.schemas import (
    DishCreateSchema,
    DishReadSchema,
    DishReadWithDiscountSchema,
)
from menu_app.utils import DishConverter


class DishService:
    """Service for dish"""

    def __init__(
            self,
            dish_repo: DishRepository = Depends(),
            dish_cache: CacheRepository = Depends(),
            menu_app_name_keys: CacheMenuAppKeys = Depends()
    ) -> None:
        self.dish_repo = dish_repo
        self.dish_cache = dish_cache
        self.menu_app_name_keys = menu_app_name_keys

    async def get_all_dishes(
            self,
            submenu_id: UUID
    ) -> list[DishReadWithDiscountSchema]:
        """Get list dishes"""
        list_dishes_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_list_dishes_key,
            submenu_id
        )
        cache_list_dishes = await self.dish_cache.get(list_dishes_key)
        dishes_discount = await self.dish_cache.get(self.menu_app_name_keys.get_dish_discount_key)
        if cache_list_dishes is not None:
            return await DishConverter.convert_dish_sequence_to_list_dish(
                cache_list_dishes, dishes_discount
            )

        list_dishes = await self.dish_repo.get_all_dishes(
            submenu_id=submenu_id
        )
        await self.dish_cache.set(list_dishes_key, list_dishes)
        return await DishConverter.convert_dish_sequence_to_list_dish(
            list_dishes, dishes_discount
        )

    async def create_dish(
            self,
            submenu_id: UUID,
            dish_payload: DishCreateSchema,
            background_tasks: BackgroundTasks
    ) -> DishReadSchema:
        """Create dish"""
        dish = await self.dish_repo.create_dish(
            dish_payload=dish_payload,
            submenu_id=submenu_id
        )
        background_tasks.add_task(
            self.dish_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_dishes_key
        )
        background_tasks.add_task(self.dish_cache.delete, [
            self.menu_app_name_keys.get_list_menus_nested_key,
        ])
        return dish

    async def get_dish(
            self,
            dish_id: UUID
    ) -> DishReadWithDiscountSchema:
        """Get dish by id"""
        dish_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_dish_key,
            dish_id
        )
        dishes_discount = await self.dish_cache.get(self.menu_app_name_keys.get_dish_discount_key)
        cache_dish = await self.dish_cache.get(dish_key)
        if cache_dish is not None:
            return await DishConverter.convert_dish_row_to_schema(cache_dish, dishes_discount)

        dish = await self.dish_repo.get_dish(
            dish_id=dish_id
        )
        await self.dish_cache.set(dish_key, dish)
        return await DishConverter.convert_dish_row_to_schema(dish, dishes_discount)

    async def update_dish(
            self,
            dish_id: UUID,
            dish_payload: DishCreateSchema,
            background_tasks: BackgroundTasks
    ) -> DishReadSchema:
        """Update dish by id"""
        dish = await self.dish_repo.update_dish(
            dish_id=dish_id,
            dish_payload=dish_payload
        )
        dish_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_dish_key,
            dish_id
        )

        background_tasks.add_task(
            self.dish_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_dishes_key
        )
        background_tasks.add_task(self.dish_cache.delete, [
            self.menu_app_name_keys.get_list_menus_nested_key,
            dish_key,
        ])
        return dish

    async def delete_dish(
            self,
            menu_id: UUID,
            submenu_id: UUID,
            dish_id: UUID,
            background_tasks: BackgroundTasks
    ) -> JSONResponse:
        """Delete dish by id"""
        response = await self.dish_repo.delete_dish(
            dish_id=dish_id
        )
        menu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_menu_key,
            menu_id
        )
        submenu_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_submenu_key,
            submenu_id
        )
        dish_key = self.menu_app_name_keys.generate_key(
            self.menu_app_name_keys.get_dish_key,
            dish_id
        )

        background_tasks.add_task(
            self.dish_cache.delete_by_pattern,
            self.menu_app_name_keys.get_list_dishes_key
        )
        background_tasks.add_task(self.dish_cache.delete, [
            self.menu_app_name_keys.get_list_menus_nested_key,
            menu_key,
            submenu_key,
            dish_key,
        ])
        return response
