"""DIsh api routers"""
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from menu_app.dish.dish_service import DishService
from menu_app.schemas import DishCreateSchema, DishReadSchema

dish_router = APIRouter(
    prefix='/api/v1',
    tags=['dish_app']
)


@dish_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=status.HTTP_200_OK,
    response_model=list[DishReadSchema],
    tags=['Dish'],
    summary='List Dishes'
)
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


@dish_router.post(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=status.HTTP_201_CREATED,
    response_model=DishReadSchema,
    tags=['Dish'],
    summary='Create Dish'
)
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


@dish_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=status.HTTP_200_OK,
    response_model=DishReadSchema,
    tags=['Dish'],
    summary='Get Dish'
)
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


@dish_router.patch(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=status.HTTP_200_OK,
    response_model=DishReadSchema,
    tags=['Dish'],
    summary='Patch Dish'
)
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


@dish_router.delete(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=status.HTTP_200_OK,
    tags=['Dish'],
    summary='Delete Dish'
)
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
