"""
Menu Repository Pattern
"""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy import select, insert, update, delete, func, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result
from starlette.responses import JSONResponse

from db.database import get_async_session
from menu_app.models import Menu, Submenu, Dish
from menu_app.schemas import MenuCreateSchema, MenuWithCounterSchema, MenuReadSchema
from menu_app.utils import model_object_2_dict


class MenuRepository:
    """
    Repository for menu queries
    """

    def __init__(
            self,
            session: AsyncSession = Depends(get_async_session)
    ) -> None:
        self.session = session

    async def _set_counter_for_menu(
            self,
            menu_id: UUID
    ):
        # TODO
        """
        Create request for compute submenus count and dishes count for menu
        Return updated menu schema with dishes_count and submenus_count argument
        """
        sub_query = select(Submenu.menu_id, (func.count(Dish.id)).label('dish_count')).select_from(Submenu). \
            join(Dish).where(Submenu.menu_id == menu_id).group_by(Submenu.menu_id).subquery().alias('submenu_result')

        stmt = select(Menu, func.count(Submenu.menu_id).label('submenus_count'),
                      func.coalesce(func.max(sub_query.c.dish_count), 0).label('dishes_count')).select_from(Menu). \
            outerjoin(sub_query).where(Menu.id == menu_id).group_by(Menu.id)

        record: Result = await self.session.execute(stmt)
        result = record.mappings().first()

        if not result:
            return await self.if_menu_exists(menu_id)

        menu = result.get('Menu')
        table_dict = await model_object_2_dict(menu,
                                               {'dishes_count': result.get('dishes_count', 0),
                                                'submenus_count': result.get('submenus_count', 0)}
                                               )

        return MenuWithCounterSchema(**table_dict)

    async def if_menu_exists(self, menu_id: UUID) -> Row:
        """
        Check if menu exists with get menu_id
        """
        record: Result = await self.session.execute(
            select(Menu).where(Menu.id == menu_id)
        )
        result = record.scalars().first()
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='menu not found'
            )
        return result

    async def get_all_menus(
            self
    ):
        """
        List menu
        """
        return (
            await self.session.execute(
                select(Menu).order_by(Menu.id)
            )
        ).scalars().all()

    async def create_menu(
            self,
            menu_payload: MenuCreateSchema
    ) -> MenuReadSchema:
        """
        Create new menu
        """
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
    ) -> MenuWithCounterSchema:
        """
        Get menu by id
        """
        return await self._set_counter_for_menu(
            menu_id=menu_id
        )

    async def update_menu(
            self,
            menu_id: UUID,
            menu_payload: MenuCreateSchema
    ) -> MenuReadSchema:
        """
        Update meny bu id
        """
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
        """
        Delete menu by id
        """
        await self.if_menu_exists(menu_id)

        await self.session.execute(
            delete(Menu)
            .where(
                Menu.id == menu_id
            )
        )
        await self.session.commit()
        return JSONResponse(
            content={'message': 'Success delete'}
        )
