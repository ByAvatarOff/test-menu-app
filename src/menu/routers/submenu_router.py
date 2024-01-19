from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse
from menu.models import Submenu
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, insert
from db.database import get_async_session
from menu.schemas import SubMenuReadSchema, SubMenuCreateSchema, SubMenuWithCounterSchema
from sqlalchemy.engine import Result
from menu.utils import if_exists_menu_and_submenu, if_exists_menu, set_counters_for_submenu
import uuid


submenu_router = APIRouter(
    prefix="/api/v1",
    tags=["submenu_app"]
)


@submenu_router.get("/menus/{menu_id}/submenus",
                    status_code=status.HTTP_200_OK,
                    response_model=list[SubMenuReadSchema])
async def list_submenus(menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    """
    List submenus
    """
    stmt = select(Submenu).where(Submenu.menu_id == menu_id).order_by(Submenu.id)
    result: Result = await session.execute(stmt)
    return result.scalars().all()


@submenu_router.post("/menus/{menu_id}/submenus",
                     status_code=status.HTTP_201_CREATED,
                     response_model=SubMenuReadSchema)
async def create_submenu(menu_id: uuid.UUID, payload: SubMenuCreateSchema,
                         session: AsyncSession = Depends(get_async_session)):
    """
    Create menu
    """
    menu = await if_exists_menu(menu_id, session)
    if isinstance(menu, JSONResponse):
        return menu

    payload_dict = payload.model_dump()
    payload_dict.update({"menu_id": menu_id})
    stmt = insert(Submenu).values(payload_dict).returning(Submenu)
    result: Result = await session.execute(stmt)
    await session.commit()
    return result.scalars().first()


@submenu_router.get("/menus/{menu_id}/submenus/{submenu_id}",
                    status_code=status.HTTP_200_OK,
                    response_model=SubMenuWithCounterSchema)
async def get_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    """
    Get submenu
    """
    submenu = await if_exists_menu_and_submenu(menu_id, submenu_id, session)
    if not submenu:
        return submenu
    menu_with_counters = await set_counters_for_submenu(session, submenu_id, submenu)
    return menu_with_counters


@submenu_router.patch("/menus/{menu_id}/submenus/{submenu_id}",
                      status_code=status.HTTP_200_OK,
                      response_model=SubMenuReadSchema)
async def update_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, payload: SubMenuCreateSchema,
                         session: AsyncSession = Depends(get_async_session)):
    """
    Update submenu
    """
    submenu = await if_exists_menu_and_submenu(menu_id, submenu_id, session)
    if isinstance(submenu, JSONResponse):
        return submenu

    stmt = update(Submenu).where((Submenu.menu_id == menu_id) & (Submenu.id == submenu_id)) \
        .values(payload.model_dump()).returning(Submenu)
    result: Result = await session.execute(stmt)
    await session.commit()
    return result.scalars().first()


@submenu_router.delete("/menus/{menu_id}/submenus/{submenu_id}",
                       status_code=status.HTTP_200_OK)
async def delete_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    """
    Delete submenu
    """
    submenu = await if_exists_menu_and_submenu(menu_id, submenu_id, session)
    if isinstance(submenu, JSONResponse):
        return submenu

    stmt = delete(Submenu).where((Submenu.menu_id == menu_id) & (Submenu.id == submenu_id))
    await session.execute(stmt)
    await session.commit()
    return JSONResponse(content={'message': 'Success delete'})
