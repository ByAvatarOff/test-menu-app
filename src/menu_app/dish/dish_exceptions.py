"""Menu exceptions"""
from fastapi import HTTPException, status


class DishExceptions:
    """Base menu exceptions"""
    async def dish_not_found_exception(self):
        """Dish not found exception"""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='dish not found'
        )

    async def dish_title_exists_exception(self):
        """Dish title_exists exception"""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Dish with get title exists'
        )
