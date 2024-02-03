"""Submenu Repository Pattern"""
from typing import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Row, RowMapping, delete, func, insert, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from db.database import get_async_session
from menu_app.menu.menu_repo import MenuRepository
from menu_app.models import Dish, Submenu
from menu_app.schemas import SubMenuCreateSchema, SubMenuReadSchema
from menu_app.submenu.submenu_exceptions import SubmenuExceptions


class SubmenuRepository:
    """Repository for Submenu queries"""

    def __init__(
            self,
            session: AsyncSession = Depends(get_async_session),
            menu_repo: MenuRepository = Depends(),
            submenu_exceptions: SubmenuExceptions = Depends()
    ) -> None:
        self.session = session
        self.menu_repo = menu_repo
        self.submenu_exceptions = submenu_exceptions

    async def _set_counters_for_submenu(
            self,
            submenu_id: UUID
    ) -> RowMapping:
        """
        Create request for compute dishes count for submenu
        Return updated submenu schema with dishes_count argument
        """
        stmt = (
            select(
                Submenu,
                (func.count(Dish.id)).label('dishes_count')
            )
            .select_from(Submenu)
            .join(Dish)
            .where(Submenu.id == submenu_id)
            .group_by(Submenu.id)
        )
        record: Result = await self.session.execute(stmt)
        result = record.mappings().first()
        if not result:
            return await self.if_submenu_exists(submenu_id=submenu_id)
        return result

    async def if_submenu_exists(
            self,
            submenu_id: UUID
    ) -> RowMapping:
        """Check if submenu exists with get submenu_id"""
        record: Result = await self.session.execute(
            select(Submenu).where(Submenu.id == submenu_id)
        )
        result = record.mappings().first()
        if not result:
            await self.submenu_exceptions.submenu_not_found_exception()
        return result

    async def check_submenu_unique(
            self,
            title: str
    ) -> Row:
        """Check submenu title unique"""
        record: Result = await self.session.execute(
            select(Submenu).where(Submenu.title == title)
        )
        result = record.scalars().first()
        if result:
            await self.submenu_exceptions.submenu_title_exists_exception()
        return result

    async def get_all_submenus(
            self,
            menu_id: UUID
    ) -> Sequence[Row]:
        """List submenu with get menu_id"""
        await self.menu_repo.if_menu_exists(menu_id=menu_id)

        return (
            await self.session.execute(
                select(Submenu)
                .where(Submenu.menu_id == menu_id)
                .order_by(Submenu.id)
            )
        ).scalars().all()

    async def create_submenu(
            self,
            menu_id: UUID,
            submenu_payload: SubMenuCreateSchema
    ) -> SubMenuReadSchema:
        """
        Create new submenu
        Only if menu exists and new title submenu unique
        """
        await self.menu_repo.if_menu_exists(menu_id=menu_id)

        submenu_payload_dict = submenu_payload.model_dump()
        await self.check_submenu_unique(title=submenu_payload_dict.get('title'))
        submenu_payload_dict.update({'menu_id': menu_id})
        result: Result = await self.session.execute(
            insert(Submenu)
            .values(
                submenu_payload_dict
            )
            .returning(Submenu)
        )
        await self.session.commit()
        return result.scalars().first()

    async def get_submenu(
            self,
            submenu_id: UUID
    ) -> RowMapping:
        """Get submenu by id"""
        return await self._set_counters_for_submenu(submenu_id)

    async def update_submenu(
            self,
            submenu_id: UUID,
            submenu_payload: SubMenuCreateSchema
    ) -> SubMenuReadSchema:
        """Update submenu bu id"""
        await self.if_submenu_exists(submenu_id)
        submenu_payload_dict = submenu_payload.model_dump()
        await self.check_submenu_unique(title=submenu_payload_dict.get('title'))
        result: Result = await self.session.execute(
            update(Submenu)
            .where(
                Submenu.id == submenu_id
            )
            .values(submenu_payload_dict)
            .returning(Submenu)
        )
        await self.session.commit()
        return result.scalars().first()

    async def delete_submenu(
            self,
            submenu_id: UUID
    ) -> JSONResponse:
        """Delete submenu by id"""
        await self.if_submenu_exists(submenu_id)

        await self.session.execute(
            delete(Submenu)
            .where(
                Submenu.id == submenu_id
            )
        )
        await self.session.commit()
        return JSONResponse(content={'message': 'Success submenu delete'})
