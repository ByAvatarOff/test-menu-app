"""
Submenu api routers
"""
from uuid import UUID
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from menu_app.schemas import SubMenuReadSchema, SubMenuCreateSchema, SubMenuWithCounterSchema
from menu_app.submenu.submenu_service import SubmenuService



submenu_router = APIRouter(
    prefix="/api/v1",
    tags=["submenu_app"]
)


@submenu_router.get("/menus/{menu_id}/submenus",
                    status_code=status.HTTP_200_OK,
                    response_model=list[SubMenuReadSchema])
async def list_submenus(
        menu_id: UUID,
        submenu_repo: SubmenuService = Depends()
) -> list[SubMenuReadSchema]:
    """
    List submenus
    """
    return await submenu_repo.get_all_submenus(
        menu_id=menu_id
    )


@submenu_router.post("/menus/{menu_id}/submenus",
                     status_code=status.HTTP_201_CREATED,
                     response_model=SubMenuReadSchema)
async def create_submenu(
        menu_id: UUID,
        payload: SubMenuCreateSchema,
        submenu_repo: SubmenuService = Depends()
) -> SubMenuReadSchema:
    """
    Create submenu
    """
    return await submenu_repo.create_submenu(
        submenu_payload=payload,
        menu_id=menu_id
    )


@submenu_router.get("/menus/{menu_id}/submenus/{submenu_id}",
                    status_code=status.HTTP_200_OK,
                    response_model=SubMenuWithCounterSchema)
async def get_submenu(
        submenu_id: UUID,
        submenu_repo: SubmenuService = Depends()
) -> SubMenuWithCounterSchema:
    """
    Get submenu
    """
    return await submenu_repo.get_submenu(
        submenu_id=submenu_id
    )


@submenu_router.patch("/menus/{menu_id}/submenus/{submenu_id}",
                      status_code=status.HTTP_200_OK,
                      response_model=SubMenuReadSchema)
async def update_submenu(
        submenu_id: UUID,
        payload: SubMenuCreateSchema,
        submenu_repo: SubmenuService = Depends()
) -> SubMenuReadSchema:
    """
    Update submenu
    """
    return await submenu_repo.update_submenu(
        submenu_id=submenu_id,
        submenu_payload=payload
    )


@submenu_router.delete("/menus/{menu_id}/submenus/{submenu_id}",
                       status_code=status.HTTP_200_OK)
async def delete_submenu(
        submenu_id: UUID,
        submenu_repo: SubmenuService = Depends()
) -> JSONResponse:
    """
    Delete submenu
    """
    return await submenu_repo.delete_submenu(
        submenu_id=submenu_id
    )
