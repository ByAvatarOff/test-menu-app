"""
DIsh api routers
"""
from uuid import UUID
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from menu_app.schemas import DishReadSchema, DishCreateSchema
from menu_app.dish.dish_service import DishService


dish_router = APIRouter(
    prefix="/api/v1",
    tags=["dish_app"]
)


@dish_router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes",
                 status_code=status.HTTP_200_OK,
                 response_model=list[DishReadSchema])
async def list_dishes(
        submenu_id: UUID,
        dish_repo: DishService = Depends()
) -> list[DishReadSchema]:
    """
    List dishes
    """
    return await dish_repo.get_all_dishes(
        submenu_id=submenu_id
    )


@dish_router.post("/menus/{menu_id}/submenus/{submenu_id}/dishes",
                  status_code=status.HTTP_201_CREATED,
                  response_model=DishReadSchema)
async def create_dish(
        submenu_id: UUID,
        payload: DishCreateSchema,
        dish_repo: DishService = Depends()
) -> DishReadSchema:
    """
    Create dish
    """
    return await dish_repo.create_submenu(
        dish_payload=payload,
        submenu_id=submenu_id
    )


@dish_router.get("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
                 status_code=status.HTTP_200_OK,
                 response_model=DishReadSchema)
async def get_dish(
        dish_id: UUID,
        dish_repo: DishService = Depends()
) -> DishReadSchema:
    """
    Get dish
    """
    return await dish_repo.get_dish(
        dish_id=dish_id
    )


@dish_router.patch("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
                   status_code=status.HTTP_200_OK,
                   response_model=DishReadSchema)
async def update_dish(
        dish_id: UUID,
        payload: DishCreateSchema,
        dish_repo: DishService = Depends()
) -> DishReadSchema:
    """
    Update dish
    """
    return await dish_repo.update_dish(
        dish_id=dish_id,
        dish_payload=payload
    )


@dish_router.delete("/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}",
                    status_code=status.HTTP_200_OK)
async def delete_dish(
        dish_id: UUID,
        dish_repo: DishService = Depends()
) -> JSONResponse:
    """
    Delete dish
    """
    return await dish_repo.delete_dish(
        dish_id=dish_id
    )
