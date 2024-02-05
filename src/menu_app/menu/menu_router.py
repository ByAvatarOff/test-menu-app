"""Menu api routers"""
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from menu_app.menu.menu_open_api_builder import MenuOpenApiBuilder
from menu_app.menu.menu_service import MenuService
from menu_app.schemas import MenuCreateSchema, MenuReadSchema, MenuWithCounterSchema

menu_router = APIRouter(
    prefix='/api/v1',
    tags=['Menu']
)


@menu_router.get(
    '/menus',
    status_code=status.HTTP_200_OK,
    response_model=list[MenuReadSchema],
    tags=MenuOpenApiBuilder.get_tag(),
    summary='List Menu'
)
async def list_menus(
        menu_service: MenuService = Depends()
) -> list[MenuReadSchema]:
    """List menus"""
    return await menu_service.get_all_menus()


@menu_router.post(
    '/menus',
    status_code=status.HTTP_201_CREATED,
    response_model=MenuReadSchema,
    tags=MenuOpenApiBuilder.get_tag(),
    summary='Create Menu',
)
async def create_menu(
        payload: MenuCreateSchema,
        menu_service: MenuService = Depends()
) -> MenuReadSchema:
    """Create menu"""
    return await menu_service.create_menu(
        menu_payload=payload
    )


@menu_router.get(
    '/menus/{menu_id}',
    status_code=status.HTTP_200_OK,
    response_model=MenuWithCounterSchema,
    tags=MenuOpenApiBuilder.get_tag(),
    summary='Get Menu',
    responses=MenuOpenApiBuilder.get_menu_not_found_404_response()
)
async def get_menu(
        menu_id: UUID,
        menu_service: MenuService = Depends()
) -> MenuWithCounterSchema:
    """Get menu"""
    return await menu_service.get_menu(
        menu_id=menu_id
    )


@menu_router.patch(
    '/menus/{menu_id}',
    status_code=status.HTTP_200_OK,
    response_model=MenuReadSchema,
    tags=MenuOpenApiBuilder.get_tag(),
    summary='Patch Menu',
    responses=MenuOpenApiBuilder.get_menu_not_found_404_response()
)
async def update_menu(
        menu_id: UUID,
        payload: MenuCreateSchema,
        menu_service: MenuService = Depends()
) -> MenuReadSchema:
    """Update menu"""
    return await menu_service.update_menu(
        menu_id=menu_id,
        menu_payload=payload
    )


@menu_router.delete(
    '/menus/{menu_id}',
    status_code=status.HTTP_200_OK,
    tags=MenuOpenApiBuilder.get_tag(),
    summary='Delete Menu',
    responses=MenuOpenApiBuilder.get_menu_not_found_404_response()
)
async def delete_menu(
        menu_id: UUID,
        menu_service: MenuService = Depends()
) -> JSONResponse:
    """Delete menu"""
    return await menu_service.delete_menu(
        menu_id=menu_id
    )
