"""DIsh service layer"""
from uuid import UUID

from fastapi import Depends
from starlette.responses import JSONResponse

from db.cache_repo import CacheMenuAppKeys, CacheRepository
from menu_app.dish.dish_repo import DishRepository
from menu_app.schemas import DishCreateSchema, DishReadSchema
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
        self.menu_name_keys = menu_app_name_keys

    async def get_all_dishes(
            self,
            submenu_id: UUID
    ) -> list[DishReadSchema]:
        """Get list dishes"""
        cache_list_dishes = await self.dish_cache.get(self.menu_name_keys.get_list_dishes_key)

        if cache_list_dishes is not None:
            return await DishConverter.convert_dish_sequence_to_list_dish(cache_list_dishes)

        list_dishes = await self.dish_repo.get_all_dishes(
            submenu_id=submenu_id
        )
        await self.dish_cache.set(self.menu_name_keys.get_list_dishes_key, list_dishes)
        return await DishConverter.convert_dish_sequence_to_list_dish(list_dishes)

    async def create_submenu(
            self,
            submenu_id: UUID,
            dish_payload: DishCreateSchema
    ) -> DishReadSchema:
        """Create dish"""
        dish = await self.dish_repo.create_dish(
            dish_payload=dish_payload,
            submenu_id=submenu_id
        )
        await self.dish_cache.delete(self.menu_name_keys.get_list_dishes_key)
        return dish

    async def get_dish(
            self,
            dish_id: UUID
    ) -> DishReadSchema:
        """Get dish by id"""
        dish = await self.dish_repo.get_dish(
            dish_id=dish_id
        )
        return await DishConverter.convert_dish_row_to_schema(dish)

    async def update_dish(
            self,
            dish_id: UUID,
            dish_payload: DishCreateSchema
    ) -> DishReadSchema:
        """Update dish by id"""
        dish = await self.dish_repo.update_dish(
            dish_id=dish_id,
            dish_payload=dish_payload
        )
        await self.dish_cache.delete(self.menu_name_keys.get_list_dishes_key)
        return dish

    async def delete_dish(
            self,
            dish_id: UUID
    ) -> JSONResponse:
        """Delete dish by id"""
        response = await self.dish_repo.delete_dish(
            dish_id=dish_id
        )
        await self.dish_cache.delete(self.menu_name_keys.get_list_dishes_key)
        return response
