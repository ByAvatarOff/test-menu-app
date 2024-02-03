"""Submenu exceptions"""
from fastapi import HTTPException, status


class SubmenuExceptions:
    """Base submenu exceptions"""
    async def submenu_not_found_exception(self):
        """Submenu not found exception"""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='submenu not found'
        )

    async def submenu_title_exists_exception(self):
        """Submenu title_exists exception"""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Submenu with get title exists'
        )
