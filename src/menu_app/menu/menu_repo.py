"""Menu Repository Pattern"""
from typing import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Row, RowMapping, delete, func, insert, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.responses import JSONResponse

from db.database import get_async_session
from menu_app.menu.menu_exceptions import MenuExceptions
from menu_app.models import Dish, Menu, Submenu
from menu_app.schemas import MenuCreateSchema, MenuReadSchema
from menu_app.utils import ModelToJson


class MenuRepository:
    """Repository for menu queries"""

    def __init__(
            self,
            session: AsyncSession = Depends(get_async_session),
            models_to_json: ModelToJson = Depends(),
            menu_exceptions: MenuExceptions = Depends(),

    ) -> None:
        self.session = session
        self.models_to_json = models_to_json
        self.menu_exceptions = menu_exceptions

    async def _set_counters_for_menu(
            self,
            menu_id: UUID
    ) -> RowMapping:
        """
        Create request for compute submenus count and dishes count for menu
        Return updated menu schema with dishes_count and submenus_count argument
        """
        sub_query = (
            select(
                Submenu.menu_id,
                (func.count(Dish.id)).label('dish_count')
            )
            .select_from(Submenu).join(Dish, Dish.submenu_id == Submenu.id)
            .where(Submenu.menu_id == menu_id)
            .group_by(Submenu.menu_id)
            .subquery().alias('submenu_res'))

        stmt = (
            select(
                Menu,
                func.count(Submenu.menu_id).label('submenus_count'),
                func.coalesce(func.max(sub_query.c.dish_count), 0).label('dishes_count')
            )
            .select_from(Menu)
            .outerjoin(sub_query, Menu.id == sub_query.c.menu_id)
            .where(Menu.id == menu_id)
            .group_by(Menu.id))

        record: Result = await self.session.execute(stmt)
        result = record.mappings().first()
        if not result:
            return await self.if_menu_exists(menu_id)
        return result

    async def if_menu_exists(self, menu_id: UUID) -> RowMapping:
        """Check if menu exists with get menu_id"""
        record: Result = await self.session.execute(
            select(Menu).where(Menu.id == menu_id)
        )
        result = record.mappings().first()
        if not result:
            await self.menu_exceptions.menu_not_found_exception()
        return result

    async def get_all_menus(
            self
    ) -> Sequence[Row]:
        """List menu"""
        return (
            await self.session.execute(
                select(Menu).order_by(Menu.id)
            )
        ).scalars().all()

    async def get_all_menus_with_nested_obj(
            self
    ) -> Sequence[Row]:
        """List nested objects with menu"""
        return (
            await self.session.execute(
                select(Menu)
                .options(selectinload(Menu.submenus)
                         .selectinload(Submenu.dish))
            )
        ).scalars().all()

    async def create_menu(
            self,
            menu_payload: MenuCreateSchema
    ) -> MenuReadSchema:
        """Create new menu"""
        result: Result = await self.session.execute(
            insert(Menu)
            .values(
                menu_payload.model_dump()
            )
            .returning(Menu)
        )
        await self.session.commit()
        return result.scalars().first()

    async def get_menu(
            self,
            menu_id: UUID
    ) -> RowMapping:
        """Get menu by id"""
        return await self._set_counters_for_menu(
            menu_id=menu_id
        )

    async def update_menu(
            self,
            menu_id: UUID,
            menu_payload: MenuCreateSchema
    ) -> MenuReadSchema:
        """Update meny bu id"""
        await self.if_menu_exists(menu_id)

        result: Result = await self.session.execute(
            update(Menu)
            .where(
                Menu.id == menu_id
            )
            .values(menu_payload.model_dump())
            .returning(Menu)
        )
        await self.session.commit()
        return result.scalars().first()

    async def delete_menu(
            self,
            menu_id: UUID
    ) -> JSONResponse:
        """Delete menu by id"""
        await self.if_menu_exists(menu_id)

        await self.session.execute(
            delete(Menu)
            .where(
                Menu.id == menu_id
            )
        )
        await self.session.commit()
        return JSONResponse(
            content={'message': 'Success menu delete'}
        )
