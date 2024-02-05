"""Submenu api routers"""
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from menu_app.menu.menu_open_api_builder import MenuOpenApiBuilder
from menu_app.schemas import (
    SubMenuCreateSchema,
    SubMenuReadSchema,
    SubMenuWithCounterSchema,
)
from menu_app.submenu.submenu_open_api_builder import SubmenuOpenApiBuilder
from menu_app.submenu.submenu_service import SubmenuService
from menu_app.utils import concat_dicts

submenu_router = APIRouter(
    prefix='/api/v1',
    tags=['Submenu']
)


@submenu_router.get(
    '/menus/{menu_id}/submenus',
    status_code=status.HTTP_200_OK,
    response_model=list[SubMenuReadSchema],
    tags=SubmenuOpenApiBuilder.get_tag(),
    summary='List Submenus',
    responses=MenuOpenApiBuilder.get_menu_not_found_404_response()
)
async def list_submenus(
        menu_id: UUID,
        submenu_service: SubmenuService = Depends()
) -> list[SubMenuReadSchema]:
    """List submenus"""
    return await submenu_service.get_all_submenus(
        menu_id=menu_id
    )


@submenu_router.post(
    '/menus/{menu_id}/submenus',
    status_code=status.HTTP_201_CREATED,
    response_model=SubMenuReadSchema,
    tags=SubmenuOpenApiBuilder.get_tag(),
    summary='Create Submenu',
    responses=concat_dicts(
        MenuOpenApiBuilder.get_menu_not_found_404_response(),
        SubmenuOpenApiBuilder.get_submenu_unique_title_400_response()
    )
)
async def create_submenu(
        menu_id: UUID,
        payload: SubMenuCreateSchema,
        submenu_service: SubmenuService = Depends()
) -> SubMenuReadSchema:
    """Create submenu"""
    return await submenu_service.create_submenu(
        submenu_payload=payload,
        menu_id=menu_id
    )


@submenu_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}',
    status_code=status.HTTP_200_OK,
    response_model=SubMenuWithCounterSchema,
    tags=SubmenuOpenApiBuilder.get_tag(),
    summary='Get Submenu',
    responses=SubmenuOpenApiBuilder.get_submenu_not_found_404_response()
)
async def get_submenu(
        submenu_id: UUID,
        submenu_service: SubmenuService = Depends()
) -> SubMenuWithCounterSchema:
    """Get submenu"""
    return await submenu_service.get_submenu(
        submenu_id=submenu_id
    )


@submenu_router.patch(
    '/menus/{menu_id}/submenus/{submenu_id}',
    status_code=status.HTTP_200_OK,
    response_model=SubMenuReadSchema,
    tags=SubmenuOpenApiBuilder.get_tag(),
    summary='Patch Submenu',
    responses=concat_dicts(
        MenuOpenApiBuilder.get_menu_not_found_404_response(),
        SubmenuOpenApiBuilder.get_submenu_unique_title_400_response()
    )
)
async def update_submenu(
        submenu_id: UUID,
        payload: SubMenuCreateSchema,
        submenu_service: SubmenuService = Depends()
) -> SubMenuReadSchema:
    """Update submenu"""
    return await submenu_service.update_submenu(
        submenu_id=submenu_id,
        submenu_payload=payload
    )


@submenu_router.delete(
    '/menus/{menu_id}/submenus/{submenu_id}',
    status_code=status.HTTP_200_OK,
    tags=SubmenuOpenApiBuilder.get_tag(),
    summary='Delete Submenu',
    responses=SubmenuOpenApiBuilder.get_submenu_not_found_404_response()
)
async def delete_submenu(
        menu_id: UUID,
        submenu_id: UUID,
        submenu_service: SubmenuService = Depends()
) -> JSONResponse:
    """Delete submenu"""
    return await submenu_service.delete_submenu(
        menu_id=menu_id,
        submenu_id=submenu_id,
    )
