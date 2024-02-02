"""
DIsh service layer
"""
from uuid import UUID
from fastapi import Depends
from starlette.responses import JSONResponse

from menu_app.dish.dish_repo import DishRepository
from menu_app.schemas import DishReadSchema, DishCreateSchema


class DishService:
    """
    Service for dish
    """
    def __init__(
            self,
            dish_repo: DishRepository = Depends()
    ) -> None:
        self.dish_repo = dish_repo

    async def get_all_dishes(
            self,
            submenu_id: UUID
    ) -> list[DishReadSchema]:
        """
        Get list dishes
        """
        return await self.dish_repo.get_all_dishes(
            submenu_id=submenu_id
        )

    async def create_submenu(
            self,
            submenu_id: UUID,
            dish_payload: DishCreateSchema
    ) -> DishReadSchema:
        """
        Create dish
        """
        return await self.dish_repo.create_dish(
            dish_payload=dish_payload,
            submenu_id=submenu_id
        )

    async def get_dish(
            self,
            dish_id: UUID
    ) -> DishReadSchema:
        """
        Get dish by id
        """
        return await self.dish_repo.get_dish(
            dish_id=dish_id
        )

    async def update_dish(
            self,
            dish_id: UUID,
            dish_payload: DishCreateSchema
    ) -> DishReadSchema:
        """
        Update dish by id
        """
        return await self.dish_repo.update_dish(
            dish_id=dish_id,
            dish_payload=dish_payload
        )

    async def delete_dish(
            self,
            dish_id: UUID
    ) -> JSONResponse:
        """
        Delete dish by id
        """
        return await self.dish_repo.delete_dish(
            dish_id=dish_id
        )
