"""Utils"""
from decimal import Decimal
from functools import reduce
from typing import Sequence

from sqlalchemy import Row, RowMapping

from menu_app.schemas import (
    DishReadWithDiscountSchema,
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
    async def return_dish_discount(
            dish_title: str,
            dishes_discount: Sequence[Row] | RowMapping | list[dict] | None
    ) -> Decimal:
        """Filter list dict of dishes discount by dish title"""
        try:
            if not dishes_discount:
                return Decimal(0)
            dish = list(filter(lambda obj: dish_title in obj.get('title'), dishes_discount))
            if not dish[0].get('discount') or float(dish[0].get('discount')) > 99:
                return Decimal(0)
            return Decimal(dish[0].get('discount'))
        except IndexError:
            return Decimal(0)

    @staticmethod
    async def convert_dish_sequence_to_list_dish(
            dishes: Sequence[Row],
            dishes_discount: Sequence[Row] | list[dict] | None
    ) -> list[DishReadWithDiscountSchema]:
        """Convert Sequence[Row] to list[DishReadSchema]"""
        dish_schemas = []
        for dish in dishes:
            discount = await DishConverter.return_dish_discount(dish.title, dishes_discount)
            dish_schemas.append(DishReadWithDiscountSchema(
                id=dish.id,
                title=dish.title,
                description=dish.description,
                price=f'{Decimal(dish.price) * (1 - (discount / 100)):.2f}',
                discount=f'{discount}%'
            ))
        return dish_schemas

    @staticmethod
    async def convert_dish_row_to_schema(
            dish_row_mapping: RowMapping,
            dishes_discount: RowMapping | list[dict] | None
    ) -> DishReadWithDiscountSchema:
        """Convert Row to DishReadSchema"""
        dish = dish_row_mapping.get('Dish')
        discount = await DishConverter.return_dish_discount(dish.title, dishes_discount)
        return DishReadWithDiscountSchema(
            id=dish.id,
            title=dish.title,
            description=dish.description,
            price=f'{Decimal(dish.price) * (1 - (discount / 100)):.2f}',
            discount=f'{discount}%'
        )


async def add_discount_to_dish(
        list_menus_nested: Sequence[Row],
        dishes_discount: list[dict]
) -> list[dict]:
    """Add to every dish discount and calculate new price"""
    list_menus_object: list = []
    for (index, menu) in enumerate(list_menus_nested):
        list_menus_object.append(
            {
                'id': menu.id, 'title': menu.title, 'description': menu.description, 'submenus': []
            })
        for (index_s, submenu) in enumerate(menu.submenus):
            list_menus_object[index].get('submenus').append(
                {'id': submenu.id, 'title': submenu.title, 'description': submenu.description, 'dish': []}
            )
            for dish in submenu.dish:
                discount = await DishConverter.return_dish_discount(dish.title, dishes_discount)
                list_menus_object[index].get('submenus')[index_s].get('dish').append(
                    {
                        'id': dish.id, 'title': dish.title, 'description': dish.description,
                        'price': f'{Decimal(dish.price) * (1 - (discount / 100)):.2f}',
                        'discount': f'{discount}%'
                    })
    return list_menus_object


def concat_dicts(*dicts: dict) -> dict:
    """Concat getting dict to one dict"""
    return reduce(lambda dict_1, dict_2: {**dict_1, **dict_2}, dicts)
