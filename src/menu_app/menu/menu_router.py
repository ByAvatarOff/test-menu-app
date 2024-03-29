"""Menu api routers"""
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from starlette import status
from starlette.responses import JSONResponse

from menu_app.menu.menu_open_api_builder import MenuOpenApiBuilder
from menu_app.menu.menu_service import MenuService
from menu_app.schemas import (
    MenuCreateSchema,
    MenuReadNested,
    MenuReadSchema,
    MenuWithCounterSchema,
)

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


@menu_router.get(
    '/nested_menus',
    status_code=status.HTTP_200_OK,
    response_model=list[MenuReadNested],
    tags=MenuOpenApiBuilder.get_tag(),
    summary='list menu with nested objects'
)
async def list_menus_with_nested_obj(
        menu_service: MenuService = Depends()
) -> list[MenuReadNested]:
    """List menus"""
    return await menu_service.list_menus_with_nested_obj()


@menu_router.post(
    '/menus',
    status_code=status.HTTP_201_CREATED,
    response_model=MenuReadSchema,
    tags=MenuOpenApiBuilder.get_tag(),
    summary='Create Menu',
)
async def create_menu(
        payload: MenuCreateSchema,
        background_tasks: BackgroundTasks,
        menu_service: MenuService = Depends()
) -> MenuReadSchema:
    """Create menu"""
    return await menu_service.create_menu(
        menu_payload=payload,
        background_tasks=background_tasks
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
        background_tasks: BackgroundTasks,
        menu_service: MenuService = Depends()
) -> MenuReadSchema:
    """Update menu"""
    return await menu_service.update_menu(
        menu_id=menu_id,
        menu_payload=payload,
        background_tasks=background_tasks,
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
        background_tasks: BackgroundTasks,
        menu_service: MenuService = Depends(),

) -> JSONResponse:
    """Delete menu"""
    return await menu_service.delete_menu(
        menu_id=menu_id,
        background_tasks=background_tasks,
    )
