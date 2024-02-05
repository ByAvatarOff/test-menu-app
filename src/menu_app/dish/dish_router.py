"""DIsh api routers"""
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from menu_app.dish.dish_open_api_builder import DishOpenApiBuilder
from menu_app.dish.dish_service import DishService
from menu_app.schemas import DishCreateSchema, DishReadSchema
from menu_app.submenu.submenu_open_api_builder import SubmenuOpenApiBuilder
from menu_app.utils import concat_dicts

dish_router = APIRouter(
    prefix='/api/v1',
    tags=['Dish']
)


@dish_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=status.HTTP_200_OK,
    response_model=list[DishReadSchema],
    tags=DishOpenApiBuilder.get_tag(),
    summary='List Dishes',
    responses=SubmenuOpenApiBuilder.get_submenu_not_found_404_response()
)
async def list_dishes(
        submenu_id: UUID,
        dish_service: DishService = Depends()
) -> list[DishReadSchema]:
    """
    List dishes
    """
    return await dish_service.get_all_dishes(
        submenu_id=submenu_id
    )


@dish_router.post(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=status.HTTP_201_CREATED,
    response_model=DishReadSchema,
    tags=DishOpenApiBuilder.get_tag(),
    summary='Create Dish',
    responses=concat_dicts(
        SubmenuOpenApiBuilder.get_submenu_not_found_404_response(),
        DishOpenApiBuilder.get_dish_unique_title_400_response()
    )
)
async def create_dish(
        submenu_id: UUID,
        payload: DishCreateSchema,
        dish_service: DishService = Depends()
) -> DishReadSchema:
    """
    Create dish
    """
    return await dish_service.create_submenu(
        dish_payload=payload,
        submenu_id=submenu_id
    )


@dish_router.get(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=status.HTTP_200_OK,
    response_model=DishReadSchema,
    tags=DishOpenApiBuilder.get_tag(),
    summary='Get Dish',
    responses=DishOpenApiBuilder.get_dish_not_found_404_response()
)
async def get_dish(
        dish_id: UUID,
        dish_service: DishService = Depends()
) -> DishReadSchema:
    """
    Get dish
    """
    return await dish_service.get_dish(
        dish_id=dish_id
    )


@dish_router.patch(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=status.HTTP_200_OK,
    response_model=DishReadSchema,
    tags=DishOpenApiBuilder.get_tag(),
    summary='Patch Dish',
    responses=concat_dicts(
        DishOpenApiBuilder.get_dish_not_found_404_response(),
        DishOpenApiBuilder.get_dish_unique_title_400_response()
    )
)
async def update_dish(
        dish_id: UUID,
        payload: DishCreateSchema,
        dish_service: DishService = Depends()
) -> DishReadSchema:
    """
    Update dish
    """
    return await dish_service.update_dish(
        dish_id=dish_id,
        dish_payload=payload
    )


@dish_router.delete(
    '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=status.HTTP_200_OK,
    tags=DishOpenApiBuilder.get_tag(),
    summary='Delete Dish',
    responses=DishOpenApiBuilder.get_dish_not_found_404_response()
)
async def delete_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_id: UUID,
        dish_service: DishService = Depends()
) -> JSONResponse:
    """
    Delete dish
    """
    return await dish_service.delete_dish(
        menu_id=menu_id,
        submenu_id=submenu_id,
        dish_id=dish_id,
    )
