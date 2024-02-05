"""Partial functional for automation create OpenAPI Documentation"""
from starlette import status

from menu_app.schemas import NotFoundRecord


class SubmenuOpenApiBuilder:
    """Class creating documentation for failed response use OpenAPI"""
    @staticmethod
    def get_submenu_not_found_404_response() -> dict:
        """get submenu not found response documentation"""
        return {
            status.HTTP_404_NOT_FOUND: {
                'description': 'Submenu not found',
                'model': NotFoundRecord
            }
        }

    @staticmethod
    def get_submenu_unique_title_400_response() -> dict:
        """get submenu not found response documentation"""
        return {
            status.HTTP_400_BAD_REQUEST: {
                'description': 'Title submenu will be unique',
                'model': NotFoundRecord
            }
        }

    @staticmethod
    def get_tag() -> list[str]:
        """get submenu tag for OpenAPI documentation"""
        return ['Submenu']
