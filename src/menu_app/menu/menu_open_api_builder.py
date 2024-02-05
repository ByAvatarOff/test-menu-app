"""Partial functional for automation create OpenAPI Documentation"""
from starlette import status

from menu_app.schemas import NotFoundRecord


class MenuOpenApiBuilder:
    """Class creating documentation for failed response use OpenAPI"""
    @staticmethod
    def get_menu_not_found_404_response() -> dict:
        """get menu not found response documentation"""
        return {
            status.HTTP_404_NOT_FOUND: {
                'description': 'Menu not found',
                'model': NotFoundRecord
            }
        }

    @staticmethod
    def get_tag() -> list[str]:
        """get menu tag for OpenAPI documentation"""
        return ['Menu']
