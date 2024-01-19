from menu.models import Submenu, Menu, Dish
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Row
from sqlalchemy.engine import Result
from starlette import status
from starlette.responses import JSONResponse
from menu.schemas import \
    MenuWithCounterSchema, \
    SubMenuWithCounterSchema, \
    MenuReadSchema, \
    SubMenuReadSchema, \
    DishReadSchema

import uuid


async def model_object_2_dict(row: Row, additional_field: dict = None) -> dict:
    """
    Convert model object or row object to dict
    """
    table_dict = {c.name: str(getattr(row, c.name)) for c in row.__table__.columns}
    if not additional_field:
        return table_dict
    table_dict.update(additional_field)
    return table_dict


async def if_exists_menu(menu_id: uuid.UUID, session: AsyncSession) -> MenuReadSchema | JSONResponse:
    """
    Check if menu with get menu_id exists
    """
    stmt = select(Menu).where(Menu.id == menu_id)
    record: Result = await session.execute(stmt)
    result: MenuReadSchema = record.scalars().first()
    if not result:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'detail': 'menu not found'})
    return result


async def if_exists_submenu(submenu_id: uuid.UUID, session: AsyncSession) -> SubMenuReadSchema | JSONResponse:
    """
    Check if submenu with get submenu_id exists
    """
    stmt = select(Submenu).where(Submenu.id == submenu_id)
    record: Result = await session.execute(stmt)
    result: SubMenuReadSchema = record.scalars().first()
    if not result:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'detail': 'submenu not found'})
    return result


async def if_exists_dish(dish_id: uuid.UUID, session: AsyncSession) -> DishReadSchema | JSONResponse:
    """
    Check if submenu with get submenu_id exists
    """
    stmt = select(Dish).where(Dish.id == dish_id)
    record: Result = await session.execute(stmt)
    result: DishReadSchema = record.scalars().first()
    if not result:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'detail': 'dish not found'})
    return result


async def if_exists_menu_and_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession) -> SubMenuReadSchema:
    """
    Check if menu and submenu with get menu_id and submenu_id exists
    """
    await if_exists_menu(menu_id, session)
    submenu = await if_exists_submenu(submenu_id, session)
    return submenu


async def if_exists_submenu_and_dish(dish_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession) -> DishReadSchema:
    """
    Check if dish and submenu with get dish_id and submenu_id exists
    """
    await if_exists_submenu(submenu_id, session)
    dish = await if_exists_dish(dish_id, session)
    return dish


async def set_counters_for_menu(session: AsyncSession, menu_id: uuid.UUID) -> MenuWithCounterSchema | MenuReadSchema:
    """
    Create request for compute submenus count and dishes count for menu
    Return updated menu schema with dishes_count and submenus_count argument
    """
    sub_query = select(Submenu.menu_id, (func.count(Dish.id)).label('dish_count')).select_from(Submenu). \
        join(Dish).group_by(Submenu.menu_id).subquery().alias('submenu_result')

    stmt = select(Menu, func.count(Submenu.menu_id).label('submenus_count'),
                  func.coalesce(func.sum(sub_query.c.dish_count), 0).label('dishes_count')).select_from(Menu). \
        outerjoin(sub_query).where(Menu.id == menu_id).group_by(Menu.id)

    record: Result = await session.execute(stmt)
    result = record.mappings().first()
    if not result:
        return await if_exists_menu(menu_id, session)
    menu = result.get('Menu')
    table_dict = await model_object_2_dict(menu,
                                           {'dishes_count': result.get('dishes_count', 0),
                                            'submenus_count': result.get('submenus_count', 0)}
                                           )

    return MenuWithCounterSchema(**table_dict)


async def set_counters_for_submenu(session: AsyncSession, submenu_id: uuid.UUID, submenu) -> SubMenuWithCounterSchema | SubMenuReadSchema:
    """
    Create request for compute dishes count for submenu
    Return updated submenu schema with dishes_count argument
    """
    stmt = select(Submenu, (func.count(Dish.id)).label('dishes_count')).select_from(Submenu). \
        join(Dish).where(Submenu.id == submenu_id).group_by(Submenu.id)
    record: Result = await session.execute(stmt)
    result = record.mappings().first()
    if not result:
        return submenu
    submenu = result.get('Submenu')
    table_dict = await model_object_2_dict(submenu,
                                           {'dishes_count': result.get('dishes_count')}
                                           )

    return SubMenuWithCounterSchema(**table_dict)
