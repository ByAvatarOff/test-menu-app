"""Menu api routers"""
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from menu_app.menu.menu_service import MenuService
from menu_app.schemas import MenuCreateSchema, MenuReadSchema, MenuWithCounterSchema

menu_router = APIRouter(
    prefix='/api/v1',
    tags=['menu_app']
)


@menu_router.get(
    '/menus',
    status_code=status.HTTP_200_OK,
    response_model=list[MenuReadSchema],
    tags=['Menu'],
    summary='List Menu'
)
async def list_menus(
        menu_repo: MenuService = Depends()
) -> list[MenuReadSchema]:
    """List menus"""
    return await menu_repo.get_all_menus()


@menu_router.post(
    '/menus',
    status_code=status.HTTP_201_CREATED,
    response_model=MenuReadSchema,
    tags=['Menu'],
    summary='Create Menu'
)
async def create_menu(
        payload: MenuCreateSchema,
        menu_repo: MenuService = Depends()
) -> MenuReadSchema:
    """Create menu"""
    return await menu_repo.create_menu(
        menu_payload=payload
    )


@menu_router.get(
    '/menus/{menu_id}',
    status_code=status.HTTP_200_OK,
    response_model=MenuWithCounterSchema,
    tags=['Menu'],
    summary='Get Menu'
)
async def get_menu(
        menu_id: UUID,
        menu_repo: MenuService = Depends()
) -> MenuWithCounterSchema:
    """Get menu"""
    return await menu_repo.get_menu(
        menu_id=menu_id
    )


@menu_router.patch(
    '/menus/{menu_id}',
    status_code=status.HTTP_200_OK,
    response_model=MenuReadSchema,
    tags=['Menu'],
    summary='Patch Menu'
)
async def update_menu(
        menu_id: UUID,
        payload: MenuCreateSchema,
        menu_repo: MenuService = Depends()
) -> MenuReadSchema:
    """Update menu"""
    return await menu_repo.update_menu(
        menu_id=menu_id,
        menu_payload=payload
    )


@menu_router.delete(
    '/menus/{menu_id}',
    status_code=status.HTTP_200_OK,
    tags=['Menu'],
    summary='Delete Menu'
)
async def delete_menu(
        menu_id: UUID,
        menu_repo: MenuService = Depends()
) -> JSONResponse:
    """Delete menu"""
    return await menu_repo.delete_menu(
        menu_id=menu_id
    )
