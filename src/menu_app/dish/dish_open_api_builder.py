"""Partial functional for automation create OpenAPI Documentation"""
from starlette import status

from menu_app.schemas import NotFoundRecord


class DishOpenApiBuilder:
    """Class creating documentation for OpenAPI"""
    @staticmethod
    def get_dish_not_found_404_response() -> dict:
        """get dish not found response documentation"""
        return {
            status.HTTP_404_NOT_FOUND: {
                'description': 'Dish not found',
                'model': NotFoundRecord
            }
        }

    @staticmethod
    def get_dish_unique_title_400_response() -> dict:
        """get dish not found response documentation"""
        return {
            status.HTTP_400_BAD_REQUEST: {
                'description': 'Title dish will be unique',
                'model': NotFoundRecord
            }
        }

    @staticmethod
    def get_tag() -> list[str]:
        """get dish tag for OpenAPI documentation"""
        return ['Dish']
