"""Dish Repository Pattern"""
from typing import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import Row, delete, insert, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from db.database import get_async_session
from menu_app.dish.dish_exceptions import DishExceptions
from menu_app.models import Dish
from menu_app.schemas import DishCreateSchema, DishReadSchema
from menu_app.submenu.submenu_service import SubmenuRepository


class DishRepository:
    """Repository for Dish queries"""

    def __init__(
            self,
            session: AsyncSession = Depends(get_async_session),
            submenu_repo: SubmenuRepository = Depends(),
            dish_exceptions: DishExceptions = Depends()
    ) -> None:
        self.session = session
        self.submenu_repo = submenu_repo
        self.dish_exceptions = dish_exceptions

    async def if_dish_exists(
            self,
            dish_id: UUID
    ) -> Row:
        """Check if dish exists with get dish_id"""
        record: Result = await self.session.execute(
            select(Dish).where(Dish.id == dish_id)
        )
        result = record.scalars().first()
        if not result:
            await self.dish_exceptions.dish_not_found_exception()
        return result

    async def check_dish_unique(
            self,
            title: str
    ) -> Row:
        """Check dish title unique"""
        record: Result = await self.session.execute(
            select(Dish).where(Dish.title == title)
        )
        result = record.scalars().first()
        if result:
            await self.dish_exceptions.dish_title_exists_exception()
        return result

    async def get_all_dishes(
            self,
            submenu_id: UUID
    ) -> Sequence[Row]:
        """List dish with get submenu_id"""
        return (
            await self.session.execute(
                select(Dish).where(Dish.submenu_id == submenu_id).order_by(Dish.id)
            )
        ).scalars().all()

    async def create_dish(
            self,
            submenu_id: UUID,
            dish_payload: DishCreateSchema
    ) -> DishReadSchema:
        """
        Create new dish
        Only if submenu exists and new title dish unique
        """
        await self.submenu_repo.if_submenu_exists(submenu_id=submenu_id)

        dish_payload_dict = dish_payload.model_dump()
        await self.check_dish_unique(title=dish_payload_dict.get('title'))
        dish_payload_dict.update({'submenu_id': submenu_id})
        result: Result = await self.session.execute(
            insert(Dish)
            .values(
                dish_payload_dict
            )
            .returning(Dish)
        )
        await self.session.commit()
        return result.scalars().first()

    async def get_dish(
            self,
            dish_id: UUID
    ) -> Row:
        """Get dish by id"""
        return await self.if_dish_exists(dish_id)

    async def update_dish(
            self,
            dish_id: UUID,
            dish_payload: DishCreateSchema
    ) -> DishReadSchema:
        """Update dish by id"""
        await self.if_dish_exists(dish_id=dish_id)
        dish_payload_dict = dish_payload.model_dump()
        await self.check_dish_unique(title=dish_payload_dict.get('title'))
        result: Result = await self.session.execute(
            update(Dish)
            .where(
                Dish.id == dish_id
            )
            .values(dish_payload_dict)
            .returning(Dish)
        )
        await self.session.commit()
        return result.scalars().first()

    async def delete_dish(
            self,
            dish_id: UUID
    ) -> JSONResponse:
        """Delete dish by id"""
        await self.if_dish_exists(dish_id)
        await self.session.execute(
            delete(Dish)
            .where(
                Dish.id == dish_id
            )
        )
        await self.session.commit()
        return JSONResponse(
            content={'message': 'Success dish delete'}
        )
