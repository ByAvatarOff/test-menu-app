from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse
from menu.models import Dish, Submenu
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, insert
from db.database import get_async_session
from menu.schemas import DishReadSchema, DishCreateSchema
from sqlalchemy.engine import Result
from menu.utils import if_exists_menu_and_submenu, if_exists_submenu_and_dish
import uuid


dish_router = APIRouter(
    prefix="/api/v1",
    tags=["dish_app"]
)


@dish_router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes",
                 status_code=status.HTTP_200_OK,
                 response_model=list[DishReadSchema])
async def list_dishes(submenu_id: uuid.UUID,
                      session: AsyncSession = Depends(get_async_session)):
    """
    List dishes
    """
    stmt = select(Dish).join(Submenu).where((Submenu.id == submenu_id)).order_by(Dish.id)
    result: Result = await session.execute(stmt)
    return result.scalars().all()


@dish_router.post("/menus/{menu_id}/submenus/{submenu_id}/dishes",
                  status_code=status.HTTP_201_CREATED,
                  response_model=DishReadSchema)
async def create_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID, payload: DishCreateSchema,
                         session: AsyncSession = Depends(get_async_session)):
    """
    Create dish
    """
    submenu = await if_exists_menu_and_submenu(menu_id, submenu_id, session)
    if isinstance(submenu, JSONResponse):
        return submenu

    payload_dict = payload.model_dump()
    payload_dict.update({"submenu_id": submenu_id})
    stmt = insert(Dish).values(payload_dict).returning(Dish)
    result: Result = await session.execute(stmt)
    await session.commit()
    return result.scalars().first()


@dish_router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
                    status_code=status.HTTP_200_OK,
                    response_model=DishReadSchema)
async def get_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    """
    Get dish
    """
    dish = await if_exists_submenu_and_dish(dish_id, submenu_id, session)
    if isinstance(dish, JSONResponse):
        return dish

    stmt = select(Dish).where((Dish.submenu_id == submenu_id) & (Dish.id == dish_id))
    record: Result = await session.execute(stmt)
    result = record.scalars().first()
    return result


@dish_router.patch("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
                      status_code=status.HTTP_200_OK,
                      response_model=DishReadSchema)
async def update_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, payload: DishCreateSchema,
                         session: AsyncSession = Depends(get_async_session)):
    """
    Update dish
    """
    dish = await if_exists_submenu_and_dish(dish_id, submenu_id, session)
    if isinstance(dish, JSONResponse):
        return dish

    stmt = update(Dish).where((Dish.submenu_id == submenu_id) & (Dish.id == dish_id)) \
        .values(payload.model_dump()).returning(Dish)
    result: Result = await session.execute(stmt)
    await session.commit()
    return result.scalars().first()


@dish_router.delete("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
                       status_code=status.HTTP_200_OK)
async def delete_dish(submenu_id: uuid.UUID, dish_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    """
    Delete dish
    """
    dish = await if_exists_submenu_and_dish(dish_id, submenu_id, session)
    if isinstance(dish, JSONResponse):
        return dish

    stmt = delete(Dish).where((Dish.submenu_id == submenu_id) & (Dish.id == dish_id))
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content={'message': 'Success delete'})
