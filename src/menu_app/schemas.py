"""Schemas for model Menu, Submenu, Dish"""
from decimal import Decimal, InvalidOperation
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer, field_validator


class NotFoundRecord(BaseModel):
    detail: str


class MenuReadSchema(BaseModel):
    """Menu read schema"""
    id: UUID
    title: str
    description: str


class MenuWithCounterSchema(BaseModel):
    """
    Menu schema for view menu with two additional parameters:
    submenus_count - count related submenus,
    dishes_count - count related dishes
    """
    id: UUID
    title: str
    description: str
    submenus_count: int = Field(default=0, alias='submenus_count')
    dishes_count: int = Field(default=0, alias='dishes_count')


class MenuCreateSchema(BaseModel):
    """Menu schema for creating menu instance"""
    title: str
    description: str


class SubMenuReadSchema(BaseModel):
    """SubMenu read schema"""
    id: UUID
    title: str
    description: str


class SubMenuWithCounterSchema(BaseModel):
    """
    SubMenu schema for view submenu with additional parameter:
    dishes_count - count related dishes
    """
    id: UUID
    title: str
    description: str
    dishes_count: int = Field(default=0, alias='dishes_count')


class SubMenuCreateSchema(BaseModel):
    """SubMenu schema for creating submenu instance"""
    title: str
    description: str


class DishReadSchema(BaseModel):
    """Dish read schema"""
    id: UUID
    title: str
    description: str
    price: str

    @field_serializer('price')
    def convert_to_2_decimal_places(self, price):
        """
        Serialize price for input
        Only two decimal_places
        """
        try:
            return f'{Decimal(price):.2f}'
        except InvalidOperation:
            raise ValueError('Invalid type price')


class DishCreateSchema(BaseModel):
    """Dish schema for creating dish instance"""
    title: str
    description: str
    price: str

    @field_validator('price')
    @classmethod
    def check_if_decimal_price(cls, value):
        """
        Validator check decimal value on field price
        IF not raise ValueError
        """
        try:
            assert Decimal(value)
            return value
        except InvalidOperation:
            raise ValueError('You must get float price')
