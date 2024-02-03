"""Menu exceptions"""
from fastapi import HTTPException, status


class MenuExceptions:
    """Base menu exceptions"""
    async def menu_not_found_exception(self):
        """Menu not found exceptions"""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='menu not found'
        )
