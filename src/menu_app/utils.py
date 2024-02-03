"""Utils"""
from typing import Sequence

from sqlalchemy import Row, RowMapping

from menu_app.schemas import (
    DishReadSchema,
    MenuReadSchema,
    MenuWithCounterSchema,
    SubMenuReadSchema,
    SubMenuWithCounterSchema,
)


class ModelToJson:
    """Class converting models to json list"""

    @staticmethod
    async def model_object_2_dict(
            row: Row,
            **kwargs: str
    ) -> dict:
        """Convert model object or row object to dict"""
        table_dict = {
            c.name: str(getattr(row, c.name))
            for c in row.__table__.columns
        }
        if not kwargs:
            return table_dict
        table_dict.update(kwargs)
        return table_dict


class MenuConverter:
    """Class for convert Menu model"""
    @staticmethod
    async def convert_menus_sequence_to_list_menus(menus: Sequence[Row]) -> list[MenuReadSchema]:
        """Convert Sequence[Row] to list[MenuReadSchema]"""
        return [
            MenuReadSchema(
                id=menu.id,
                title=menu.title,
                description=menu.description
            )
            for menu in menus
        ]

    @staticmethod
    async def convert_menu_row_to_schema(
            menu_row_mapping: RowMapping,
    ) -> MenuWithCounterSchema:
        """Convert Sequence[Row] to MenuWithCounterSchema"""
        menu = menu_row_mapping.get('Menu')
        return MenuWithCounterSchema(
            id=menu.id,
            title=menu.title,
            description=menu.description,
            dishes_count=menu_row_mapping.get('dishes_count', 0),
            submenus_count=menu_row_mapping.get('submenus_count', 0)
        )


class SubmenuConverter:
    """Class for convert Submenu model"""
    @staticmethod
    async def convert_submenus_sequence_to_list_submenus(submenus: Sequence[Row]) -> list[SubMenuReadSchema]:
        """Convert Sequence[Row] to list[SubMenuReadSchema]"""
        return [
            SubMenuReadSchema(
                id=submenu.id,
                title=submenu.title,
                description=submenu.description
            )
            for submenu in submenus
        ]

    @staticmethod
    async def convert_submenu_row_to_schema(
            submenu_row_mapping: RowMapping,
    ) -> SubMenuWithCounterSchema:
        """Convert Sequence[Row] to SubMenuWithCounterSchema"""
        submenu = submenu_row_mapping.get('Submenu')
        return SubMenuWithCounterSchema(
            id=submenu.id,
            title=submenu.title,
            description=submenu.description,
            dishes_count=submenu_row_mapping.get('dishes_count', 0),
        )


class DishConverter:
    """Class for convert Dish model"""
    @staticmethod
    async def convert_dish_sequence_to_list_dish(dishes: Sequence[Row]) -> list[DishReadSchema]:
        """Convert Sequence[Row] to list[DishReadSchema]"""
        return [
            DishReadSchema(
                id=dish.id,
                title=dish.title,
                description=dish.description,
                price=dish.price
            )
            for dish in dishes
        ]

    @staticmethod
    async def convert_dish_row_to_schema(dish: Row) -> DishReadSchema:
        """Convert Row to DishReadSchema"""
        return DishReadSchema(
            id=dish.id,
            title=dish.title,
            description=dish.description,
            price=dish.price
        )
