"""
Submenu service layer
"""
from uuid import UUID

from fastapi import Depends
from starlette.responses import JSONResponse

from menu_app.submenu.submenu_repo import SubmenuRepository
from menu_app.schemas import  SubMenuReadSchema, SubMenuCreateSchema, SubMenuWithCounterSchema


class SubmenuService:
    """
    Service for menu
    """

    def __init__(
            self,
            submenu_repo: SubmenuRepository = Depends()
    ) -> None:
        self.submenu_repo = submenu_repo

    async def get_all_submenus(
            self,
            menu_id: UUID
    ) -> list[SubMenuReadSchema]:
        """
        Get list submenu
        """
        return await self.submenu_repo.get_all_submenus(
            menu_id=menu_id
        )

    async def create_submenu(
            self,
            menu_id: UUID,
            submenu_payload: SubMenuCreateSchema
    ) -> SubMenuReadSchema:
        """
        Create menu
        """
        return await self.submenu_repo.create_submenu(
            submenu_payload=submenu_payload,
            menu_id=menu_id
        )

    async def get_submenu(
            self,
            submenu_id: UUID
    ) -> SubMenuWithCounterSchema:
        """
        Get submenu by id
        """
        return await self.submenu_repo.get_submenu(
            submenu_id=submenu_id
        )

    async def update_submenu(
            self,
            submenu_id: UUID,
            submenu_payload: SubMenuCreateSchema
    ) -> SubMenuReadSchema:
        """
        Update submenu by id
        """
        return await self.submenu_repo.update_submenu(
            submenu_id=submenu_id,
            submenu_payload=submenu_payload
        )

    async def delete_submenu(
            self,
            submenu_id: UUID
    ) -> JSONResponse:
        """
        Delete submenu by id
        """
        return await self.submenu_repo.delete_submenu(
            submenu_id=submenu_id
        )
