"""
Menu service layer
"""
from uuid import UUID
from fastapi import Depends
from starlette.responses import JSONResponse

from menu_app.menu.menu_repo import MenuRepository
from menu_app.schemas import MenuReadSchema, MenuCreateSchema, MenuWithCounterSchema


class MenuService:
    """
    Service for menu
    """
    def __init__(
            self,
            menu_repo: MenuRepository = Depends()
    ) -> None:

        self.menu_repo = menu_repo

    async def get_all_menus(
            self
    ) -> list[MenuReadSchema]:
        """
        Get list menu
        """

        return await self.menu_repo.get_all_menus()

    async def create_menu(
            self,
            menu_payload: MenuCreateSchema
    ) -> MenuReadSchema:
        """
        Create menu
        """
        return await self.menu_repo.create_menu(
            menu_payload=menu_payload
        )

    async def get_menu(
            self,
            menu_id: UUID
    ) -> MenuWithCounterSchema:
        """
        Get menu by id
        """
        return await self.menu_repo.get_menu(
            menu_id=menu_id
        )

    async def update_menu(
            self,
            menu_id: UUID,
            menu_payload: MenuCreateSchema
    ) -> MenuReadSchema:
        """
        Update menu by id
        """
        return await self.menu_repo.update_menu(
            menu_id=menu_id,
            menu_payload=menu_payload
        )

    async def delete_menu(
            self,
            menu_id: UUID
    ) -> JSONResponse:
        """
        Delete menu by id
        """
        return await self.menu_repo.delete_menu(
            menu_id=menu_id
        )
