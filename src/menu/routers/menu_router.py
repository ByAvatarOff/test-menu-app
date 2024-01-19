from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse
from menu.models import Menu
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, insert
from db.database import get_async_session
from menu.schemas import MenuReadSchema, MenuCreateSchema, MenuWithCounterSchema
from sqlalchemy.engine import Result
from menu.utils import if_exists_menu, set_counters_for_menu
import uuid



menu_router = APIRouter(
    prefix="/api/v1",
    tags=["menu_app"]
)

@menu_router.get("/menus",
                 status_code=status.HTTP_200_OK,
                 response_model=list[MenuReadSchema])
async def list_menus(session: AsyncSession = Depends(get_async_session)):
    """
    List menus
    """
    stmt = select(Menu).order_by(Menu.id)
    result: Result = await session.execute(stmt)
    return result.scalars().all()


@menu_router.post("/menus",
                  status_code=status.HTTP_201_CREATED,
                  response_model=MenuReadSchema)
async def create_menu(payload: MenuCreateSchema, session: AsyncSession = Depends(get_async_session)):
    """
    Create menu
    """
    stmt = insert(Menu).values(payload.model_dump()).returning(Menu)
    result: Result = await session.execute(stmt)
    await session.commit()
    return result.scalars().first()


@menu_router.get("/menus/{menu_id}",
                 status_code=status.HTTP_200_OK,
                 response_model=MenuWithCounterSchema)
async def get_menu(menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    """
    Get menu
    """
    menu = await if_exists_menu(menu_id, session)
    if not menu:
        return menu
    menu_with_counters = await set_counters_for_menu(session, menu_id)
    return menu_with_counters


@menu_router.patch("/menus/{menu_id}",
                   status_code=status.HTTP_200_OK,
                   response_model=MenuReadSchema)
async def update_menu(menu_id: uuid.UUID, payload: MenuCreateSchema, session: AsyncSession = Depends(get_async_session)):
    """
    Update menu
    """
    menu = await if_exists_menu(menu_id, session)
    if isinstance(menu, JSONResponse):
        return menu

    stmt = update(Menu).where(Menu.id == menu_id).values(payload.model_dump()).returning(Menu)
    result: Result = await session.execute(stmt)
    await session.commit()
    return result.scalars().first()


@menu_router.delete("/menus/{menu_id}",
                    status_code=status.HTTP_200_OK)
async def delete_menu(menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    """
    Delete menu
    """
    menu = await if_exists_menu(menu_id, session)
    if isinstance(menu, JSONResponse):
        return menu

    stmt = delete(Menu).where(Menu.id == menu_id)
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content={'message': 'Success delete'})