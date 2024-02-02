"""
Submenu Repository Pattern
"""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from starlette.responses import JSONResponse

from db.database import get_async_session
from menu_app.models import Submenu, Dish
from menu_app.schemas import SubMenuCreateSchema, \
    SubMenuWithCounterSchema, SubMenuReadSchema
from menu_app.utils import model_object_2_dict
from menu_app.menu.menu_repo import MenuRepository


class SubmenuRepository:
    """
    Repository for Submenu queries
    """
    def __init__(
            self,
            session: AsyncSession = Depends(get_async_session),
            menu_repo: MenuRepository = Depends()
    ) -> None:
        self.session = session
        self.menu_repo = menu_repo

    async def _set_counters_for_submenu(
            self,
            submenu_id: UUID
    ):
        """
        Create request for compute dishes count for submenu
        Return updated submenu schema with dishes_count argument
        """
        submenu = await self.if_submenu_exists(submenu_id)

        stmt = select(
            Submenu,
            (func.count(Dish.id)).label('dishes_count')
        )\
            .select_from(Submenu)\
            .join(Dish)\
            .where(Submenu.id == submenu_id)\
            .group_by(Submenu.id)

        record: Result = await self.session.execute(stmt)
        result = record.mappings().first()
        if not result:
            return submenu
        submenu = result.get('Submenu')
        table_dict = await model_object_2_dict(submenu,
                                               {'dishes_count': result.get('dishes_count')}
                                               )

        return SubMenuWithCounterSchema(**table_dict)

    async def if_submenu_exists(
            self,
            submenu_id: UUID
    ):
        """
        Check if submenu exists with get submenu_id
        """
        record: Result = await self.session.execute(
            select(Submenu).where(Submenu.id == submenu_id)
        )
        result = record.scalars().first()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='submenu not found'
            )
        return result

    async def check_submenu_unique(
            self,
            title: str
    ):
        """
        Check submenu title unique
        """
        record: Result = await self.session.execute(
            select(Submenu).where(Submenu.title == title)
        )
        result = record.scalars().first()
        if result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Submenu with get title exists'
            )
        return result

    async def get_all_submenus(
            self,
            menu_id: UUID
    ):
        """
        List submenu with get menu_id
        """
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
        submenu_payload_dict.update({"menu_id": menu_id})
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
    ) -> SubMenuWithCounterSchema:
        """
        Get submenu by id
        """
        return await self._set_counters_for_submenu(submenu_id)

    async def update_submenu(
            self,
            submenu_id: UUID,
            submenu_payload: SubMenuCreateSchema
    ) -> SubMenuReadSchema:
        """
        Update submenu bu id
        """
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
        """
        Delete submenu by id
        """
        await self.if_submenu_exists(submenu_id)

        await self.session.execute(
            delete(Submenu)
            .where(
                Submenu.id == submenu_id
            )
        )
        await self.session.commit()
        return JSONResponse(content={'message': 'Success delete'})
